"""Orçamentos por cartão e categoria (T-054, T-055, T-057).

Regras (`spec.md` §6.13):

- a combinação usuário + cartão + mês + categoria é única;
- `Restante = Orçamento − Gastos`, com gastos somando as compras
  lançadas no cartão no **mês da data da compra** (decisão do produto:
  o abatimento no orçamento é imediato, como nas demais movimentações);
  o ciclo da fatura continua valendo para o dashboard (a fatura conta no
  mês do seu vencimento, `spec.md` §7.2);
- sem orçamento cadastrado, a categoria é exibida como "Não definido",
  sem assumir zero (AC-072);
- percentual de utilização só para orçamento maior que zero (T-058);
- restante negativo indica orçamento ultrapassado.

Os gastos nunca são materializados: derivam sempre das compras, por
isso inclusão/edição/exclusão de compra atualiza o orçamento
automaticamente (AC-074). Pagamento de fatura não é compra e nunca
entra nos gastos (T-057).
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import (
    CardCategoryBudget,
    Category,
    CreditCardPurchase,
    User,
)
from app.schemas.budget import (
    BudgetCreate,
    BudgetRecurrenceCreate,
    BudgetSeriesCreateCard,
    BudgetUpdate,
)
from app.services.cards import get_owned_card, get_owned_category

ZERO = Decimal("0.00")
CENTS = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(str(value if value is not None else 0)).quantize(
        CENTS, rounding=ROUND_HALF_UP
    )


def month_date(month: str) -> date:
    try:
        return date.fromisoformat(f"{month}-01")
    except ValueError as exc:
        raise AppError(
            code="invalid_month",
            message="Mês inválido. Use o formato AAAA-MM, com mês entre 01 e 12.",
            http_status=422,
        ) from exc


def month_str(reference_month: date) -> str:
    return f"{reference_month.year:04d}-{reference_month.month:02d}"


def summary(db: Session, user: User, card_id: int, month: str) -> dict:
    """Resumo do orçamento do cartão no mês (T-054, AC-075).

    Linhas = categorias orçadas + categorias com gastos no mês sem
    orçamento (exibidas como "Não definido").
    """
    get_owned_card(db, user, card_id)
    reference_month = month_date(month)

    budgets = list(
        db.scalars(
            select(CardCategoryBudget)
            .where(
                CardCategoryBudget.user_id == user.id,
                CardCategoryBudget.credit_card_id == card_id,
                CardCategoryBudget.reference_month == reference_month,
            )
            .order_by(CardCategoryBudget.category_id)
        )
    )
    spent_by_category = _spent_by_category(db, user, card_id, reference_month)
    recurrence_by_id = _recurrence_info(db, budgets)

    category_ids = {budget.category_id for budget in budgets} | set(spent_by_category)
    names = category_names(db, user, category_ids)

    rows = []
    for category_id in sorted(category_ids, key=lambda cid: names[cid]):
        budget = next(
            (item for item in budgets if item.category_id == category_id), None
        )
        spent = money(spent_by_category.get(category_id, ZERO))
        rows.append(
            row_payload(
                budget_id=budget.id if budget else None,
                category_id=category_id,
                category_name=names[category_id],
                budget_amount=money(budget.budget_amount) if budget else None,
                spent=spent,
                recurrence=recurrence_by_id.get(budget.id) if budget else None,
            )
        )

    total_budget = money(
        sum(
            (row["budget_amount"] if row["budget_amount"] is not None else ZERO)
            for row in rows
        )
    )
    total_spent = money(sum(row["spent"] for row in rows))
    total_remaining = money(
        sum(
            (row["remaining"] if row["remaining"] is not None else ZERO) for row in rows
        )
    )

    return {
        "month": month,
        "card_id": card_id,
        "rows": rows,
        "totals": {
            "budget_amount": total_budget,
            "spent": total_spent,
            "remaining": total_remaining,
        },
    }


def create_budget(db: Session, user: User, payload: BudgetCreate) -> dict:
    get_owned_card(db, user, payload.card_id)
    category = validate_expense_category(db, user, payload.category_id)
    reference_month = month_date(payload.month)

    existing = db.scalar(
        select(CardCategoryBudget).where(
            CardCategoryBudget.user_id == user.id,
            CardCategoryBudget.credit_card_id == payload.card_id,
            CardCategoryBudget.category_id == category.id,
            CardCategoryBudget.reference_month == reference_month,
        )
    )
    if existing is not None:
        raise AppError(
            code="budget_already_exists",
            message=(
                "Já existe orçamento para esta categoria, cartão e mês. "
                "Edite o orçamento existente."
            ),
            http_status=400,
        )

    budget = CardCategoryBudget(
        user_id=user.id,
        credit_card_id=payload.card_id,
        category_id=category.id,
        reference_month=reference_month,
        budget_amount=payload.budget_amount,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return _budget_payload(db, user, budget)


def update_budget(
    db: Session, user: User, budget_id: int, payload: BudgetUpdate
) -> dict:
    budget = _get_owned_budget(db, user, budget_id)
    budget.budget_amount = payload.budget_amount
    db.commit()
    db.refresh(budget)
    return _budget_payload(db, user, budget)


def delete_budget(db: Session, user: User, budget_id: int) -> None:
    """Remove o orçamento (AC-073); as compras são preservadas."""
    budget = _get_owned_budget(db, user, budget_id)
    db.delete(budget)
    db.commit()


def _get_owned_budget(db: Session, user: User, budget_id: int) -> CardCategoryBudget:
    budget = db.scalar(
        select(CardCategoryBudget).where(
            CardCategoryBudget.id == budget_id,
            CardCategoryBudget.user_id == user.id,
        )
    )
    if budget is None:
        raise AppError(
            code="budget_not_found",
            message="Orçamento não encontrado.",
            http_status=404,
        )
    return budget


def validate_expense_category(db: Session, user: User, category_id: int) -> Category:
    """Categoria de despesa, ativa e do usuário (T-055, `spec.md` §6.13)."""
    category = get_owned_category(db, user, category_id)
    if not category.is_active:
        raise AppError(
            code="inactive_category",
            message="A categoria está inativa. Reative-a ou escolha outra categoria.",
            http_status=400,
        )
    if category.group_type != "expense":
        raise AppError(
            code="category_type_mismatch",
            message="A categoria escolhida não é do tipo despesa.",
            http_status=400,
        )
    return category


def month_after(reference_month: date) -> date:
    """Primeiro dia do mês seguinte à referência."""
    if reference_month.month == 12:
        return date(reference_month.year + 1, 1, 1)
    return date(reference_month.year, reference_month.month + 1, 1)


def _spent_by_category(
    db: Session, user: User, card_id: int, reference_month: date
) -> dict[int, Decimal]:
    """Gastos por categoria no mês: compras lançadas no cartão no mês
    da data da compra.

    O abatimento no orçamento é imediato (mês da compra); a atribuição
    à fatura define apenas em qual fatura — e em qual mês do dashboard —
    a compra consolida (`spec.md` §7.2). Cada compra conta uma única vez
    e o pagamento de fatura nunca entra nos gastos (T-057).
    """
    next_month = month_after(reference_month)
    rows = db.execute(
        select(
            CreditCardPurchase.category_id,
            func.coalesce(func.sum(CreditCardPurchase.total_amount), ZERO),
        )
        .where(
            CreditCardPurchase.user_id == user.id,
            CreditCardPurchase.credit_card_id == card_id,
            CreditCardPurchase.purchase_date >= reference_month,
            CreditCardPurchase.purchase_date < next_month,
        )
        .group_by(CreditCardPurchase.category_id)
    ).all()
    return {category_id: Decimal(total) for category_id, total in rows}


def category_names(db: Session, user: User, category_ids: set[int]) -> dict[int, str]:
    rows = db.execute(
        select(Category.id, Category.name).where(
            Category.user_id == user.id, Category.id.in_(category_ids)
        )
    ).all()
    return dict(rows)


def row_payload(
    budget_id: int | None,
    category_id: int,
    category_name: str,
    budget_amount: Decimal | None,
    spent: Decimal,
    recurrence: dict | None = None,
) -> dict:
    """Linha do orçamento (AC-068 a AC-072).

    Sem orçamento: restante e percentual ficam nulos ("Não definido").
    Percentual só para orçamento > 0 (T-058). `recurrence` identifica a
    série quando a linha foi gerada por recorrência (T-075).
    """
    remaining = None
    usage_percent = None
    if budget_amount is not None:
        remaining = money(budget_amount - spent)
        if budget_amount > ZERO:
            usage_percent = round(float(spent / budget_amount * 100), 1)
    return {
        "id": budget_id,
        "category_id": category_id,
        "category_name": category_name,
        "budget_amount": budget_amount,
        "spent": spent,
        "remaining": remaining,
        "usage_percent": usage_percent,
        "recurrence": recurrence,
    }


def _budget_payload(db: Session, user: User, budget: CardCategoryBudget) -> dict:
    spent = _spent_by_category(
        db, user, budget.credit_card_id, budget.reference_month
    ).get(budget.category_id, ZERO)
    name = category_names(db, user, {budget.category_id})[budget.category_id]
    return row_payload(
        budget_id=budget.id,
        category_id=budget.category_id,
        category_name=name,
        budget_amount=money(budget.budget_amount),
        spent=money(spent),
        recurrence=_recurrence_info(db, [budget]).get(budget.id),
    )


def _recurrence_info(db: Session, budgets: list) -> dict[int, dict]:
    # Import local: budget_recurrences importa helpers deste módulo.
    from app.services import budget_recurrences

    return budget_recurrences.row_recurrences(db, budgets)


def create_budget_series(
    db: Session, user: User, payload: BudgetSeriesCreateCard
) -> dict:
    """Cria série de orçamentos por cartão (T-075, AC-116 a AC-118)."""
    from app.services import budget_recurrences

    record, budgets = budget_recurrences.create_series(
        db,
        user,
        category_id=payload.category_id,
        month=payload.month,
        recurrence=payload.recurrence,
        budget_model=CardCategoryBudget,
        credit_card_id=payload.card_id,
    )
    return {
        "recurrence": budget_recurrences.recurrence_payload(record),
        "months": [month_str(budget.reference_month) for budget in budgets],
        "rows": [_budget_payload(db, user, budget) for budget in budgets],
    }


def attach_budget_series(
    db: Session, user: User, budget_id: int, recurrence: BudgetRecurrenceCreate
) -> dict:
    """Ativa ou reconfigura a recorrência a partir do mês do orçamento
    do cartão (edição de orçamento)."""
    from app.services import budget_recurrences

    budget = _get_owned_budget(db, user, budget_id)
    record, rows = budget_recurrences.attach_series(
        db,
        user,
        budget,
        recurrence=recurrence,
        budget_model=CardCategoryBudget,
    )
    return {
        "recurrence": budget_recurrences.recurrence_payload(record),
        "months": [month_str(row.reference_month) for row in rows],
        "rows": [_budget_payload(db, user, row) for row in rows],
    }


def delete_budget_series(db: Session, user: User, recurrence_id: int) -> None:
    """Exclui a série de orçamentos do cartão e suas linhas (AC-119)."""
    from app.services import budget_recurrences

    budget_recurrences.delete_series(db, user, recurrence_id, general=False)
