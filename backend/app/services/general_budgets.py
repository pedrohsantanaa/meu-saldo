"""Orçamento mensal por categoria, sem cartão (T-074).

Regras (`spec.md` §6.13):

- a combinação usuário + categoria + mês é única;
- `Restante = Orçamento − Gastos`, com gastos somando as movimentações
  comuns (tipo despesa) da categoria lançadas no mês (`spec.md` §7.2):
  compras no cartão nunca contam aqui (AC-114) — abatem apenas o
  orçamento do próprio cartão, no mês da data da compra;
- despesas fixas e variáveis usam o mesmo mecanismo, conforme o grupo
  da categoria (só categorias de despesa aceitam orçamento);
- sem orçamento cadastrado, a categoria é exibida como "Não definido",
  sem assumir zero (AC-113);
- percentual de utilização só para orçamento maior que zero (T-058);
- restante negativo indica orçamento ultrapassado.

Os gastos nunca são materializados: derivam sempre das movimentações,
por isso inclusão/edição/exclusão de movimentação atualiza o orçamento
automaticamente.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import CategoryBudget, Transaction, User
from app.schemas.budget import (
    BudgetCreateGeneral,
    BudgetRecurrenceCreate,
    BudgetSeriesCreate,
    BudgetUpdate,
)
from app.services.budgets import (
    ZERO,
    category_names,
    money,
    month_after,
    month_date,
    month_str,
    row_payload,
    validate_expense_category,
)


def summary(db: Session, user: User, month: str) -> dict:
    """Resumo do orçamento sem cartão no mês (AC-111 a AC-113).

    Linhas = categorias orçadas + categorias com gastos no mês sem
    orçamento (exibidas como "Não definido").
    """
    reference_month = month_date(month)

    budgets = list(
        db.scalars(
            select(CategoryBudget)
            .where(
                CategoryBudget.user_id == user.id,
                CategoryBudget.reference_month == reference_month,
            )
            .order_by(CategoryBudget.category_id)
        )
    )
    spent_by_category = _spent_by_category(db, user, reference_month)
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
        "rows": rows,
        "totals": {
            "budget_amount": total_budget,
            "spent": total_spent,
            "remaining": total_remaining,
        },
    }


def create_budget(db: Session, user: User, payload: BudgetCreateGeneral) -> dict:
    category = validate_expense_category(db, user, payload.category_id)
    reference_month = month_date(payload.month)

    existing = db.scalar(
        select(CategoryBudget).where(
            CategoryBudget.user_id == user.id,
            CategoryBudget.category_id == category.id,
            CategoryBudget.reference_month == reference_month,
        )
    )
    if existing is not None:
        raise AppError(
            code="budget_already_exists",
            message=(
                "Já existe orçamento para esta categoria e mês. "
                "Edite o orçamento existente."
            ),
            http_status=400,
        )

    budget = CategoryBudget(
        user_id=user.id,
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
    """Remove o orçamento; as movimentações são preservadas."""
    budget = _get_owned_budget(db, user, budget_id)
    db.delete(budget)
    db.commit()


def _get_owned_budget(db: Session, user: User, budget_id: int) -> CategoryBudget:
    budget = db.scalar(
        select(CategoryBudget).where(
            CategoryBudget.id == budget_id,
            CategoryBudget.user_id == user.id,
        )
    )
    if budget is None:
        raise AppError(
            code="budget_not_found",
            message="Orçamento não encontrado.",
            http_status=404,
        )
    return budget


def _spent_by_category(
    db: Session, user: User, reference_month: date
) -> dict[int, Decimal]:
    """Gastos por categoria no mês (AC-112): movimentações comuns de
    despesa lançadas dentro do mês (`spec.md` §7.2). Compras no cartão
    ficam de fora (AC-114)."""
    next_month = month_after(reference_month)
    rows = db.execute(
        select(
            Transaction.category_id,
            func.coalesce(func.sum(Transaction.amount), ZERO),
        )
        .where(
            Transaction.user_id == user.id,
            Transaction.type == "expense",
            Transaction.transaction_date >= reference_month,
            Transaction.transaction_date < next_month,
        )
        .group_by(Transaction.category_id)
    ).all()
    return {category_id: Decimal(total) for category_id, total in rows}


def _budget_payload(db: Session, user: User, budget: CategoryBudget) -> dict:
    spent = _spent_by_category(db, user, budget.reference_month).get(
        budget.category_id, ZERO
    )
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
    # Import local: budget_recurrences importa helpers de budgets.
    from app.services import budget_recurrences

    return budget_recurrences.row_recurrences(db, budgets)


def create_budget_series(db: Session, user: User, payload: BudgetSeriesCreate) -> dict:
    """Cria série de orçamentos gerais (T-075, AC-116 a AC-118)."""
    from app.services import budget_recurrences

    record, budgets = budget_recurrences.create_series(
        db,
        user,
        category_id=payload.category_id,
        month=payload.month,
        recurrence=payload.recurrence,
        budget_model=CategoryBudget,
        credit_card_id=None,
    )
    return {
        "recurrence": budget_recurrences.recurrence_payload(record),
        "months": [month_str(budget.reference_month) for budget in budgets],
        "rows": [_budget_payload(db, user, budget) for budget in budgets],
    }


def delete_budget_series(db: Session, user: User, recurrence_id: int) -> None:
    """Exclui a série geral e suas linhas (AC-119)."""
    from app.services import budget_recurrences

    budget_recurrences.delete_series(db, user, recurrence_id, general=True)


def attach_budget_series(
    db: Session, user: User, budget_id: int, recurrence: BudgetRecurrenceCreate
) -> dict:
    """Ativa ou reconfigura a recorrência a partir do mês do orçamento
    geral (edição de orçamento)."""
    from app.services import budget_recurrences

    budget = _get_owned_budget(db, user, budget_id)
    record, rows = budget_recurrences.attach_series(
        db,
        user,
        budget,
        recurrence=recurrence,
        budget_model=CategoryBudget,
    )
    return {
        "recurrence": budget_recurrences.recurrence_payload(record),
        "months": [month_str(row.reference_month) for row in rows],
        "rows": [_budget_payload(db, user, row) for row in rows],
    }
