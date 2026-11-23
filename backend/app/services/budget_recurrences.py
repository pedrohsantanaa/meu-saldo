"""Recorrência de orçamento: parcelas e repetição mensal (T-075).

Regras (`spec.md` §6.13):

- modo "installments": `amount` é o valor TOTAL, dividido em `count`
  parcelas mensais com soma exata — as primeiras parcelas são o total
  truncado em centavos e a última absorve a diferença (`spec.md` §7.3);
- modo "monthly": `amount` é o valor MENSAL, repetido por `count` meses;
- os meses seguem a partir do mês inicial (inclusive) e o horizonte é
  sempre fixo (2 a 60 meses, sem repetição indefinida);
- a criação é atômica: se algum mês da série já tiver orçamento do
  mesmo escopo e categoria, nada é criado e os meses em conflito são
  informados (AC-118);
- cada mês gerado vira uma linha de orçamento comum, editável e
  removível mês a mês sem propagação (AC-120); a exclusão da série
  remove todas as linhas geradas (AC-119).
"""

from datetime import date
from decimal import ROUND_DOWN, Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import (
    BudgetRecurrence,
    CardCategoryBudget,
    CategoryBudget,
    User,
)
from app.schemas.budget import BudgetRecurrenceCreate
from app.services.budgets import (
    CENTS,
    money,
    month_date,
    month_str,
    validate_expense_category,
)
from app.services.cards import get_owned_card


def add_months(reference_month: date, count: int) -> date:
    """Soma `count` meses à referência, sempre no primeiro dia do mês."""
    month_index = reference_month.year * 12 + (reference_month.month - 1) + count
    return date(month_index // 12, month_index % 12 + 1, 1)


def series_months(start_month: date, count: int) -> list[date]:
    return [add_months(start_month, offset) for offset in range(count)]


def split_amounts(total: Decimal, count: int) -> list[Decimal]:
    """Divide o valor total em `count` parcelas com soma exata (§7.3):
    as primeiras parcelas são o total truncado em centavos e a última
    absorve a diferença de arredondamento."""
    total = money(total)
    base = (total / count).quantize(CENTS, rounding=ROUND_DOWN)
    amounts = [base] * (count - 1)
    amounts.append(money(total - base * (count - 1)))
    return amounts


def create_series(
    db: Session,
    user: User,
    *,
    category_id: int,
    month: str,
    recurrence: BudgetRecurrenceCreate,
    budget_model,
    credit_card_id: int | None = None,
) -> tuple[BudgetRecurrence, list]:
    """Cria a série de forma atômica (AC-116 a AC-118) e retorna o
    registro da recorrência e as linhas geradas."""
    if credit_card_id is not None:
        get_owned_card(db, user, credit_card_id)
    category = validate_expense_category(db, user, category_id)
    start_month = month_date(month)
    months = series_months(start_month, recurrence.count)

    conflicts = _conflict_months(
        db, user, budget_model, category.id, months, credit_card_id
    )
    if conflicts:
        raise AppError(
            code="budget_already_exists",
            message=(
                "Já existe orçamento em meses da série. Ajuste o mês inicial "
                "ou edite os meses existentes."
            ),
            http_status=400,
            details={"months": conflicts},
        )

    amounts = (
        split_amounts(recurrence.amount, recurrence.count)
        if recurrence.mode == "installments"
        else [money(recurrence.amount)] * recurrence.count
    )

    record = BudgetRecurrence(
        user_id=user.id,
        credit_card_id=credit_card_id,
        category_id=category.id,
        mode=recurrence.mode,
        amount=money(recurrence.amount),
        count=recurrence.count,
        start_month=start_month,
    )
    db.add(record)
    db.flush()

    rows = []
    for reference_month, amount in zip(months, amounts, strict=True):
        budget = budget_model(
            user_id=user.id,
            category_id=category.id,
            reference_month=reference_month,
            budget_amount=amount,
            recurrence_id=record.id,
        )
        if credit_card_id is not None:
            budget.credit_card_id = credit_card_id
        db.add(budget)
        rows.append(budget)
    db.commit()
    for budget in rows:
        db.refresh(budget)
    return record, rows


def delete_series(
    db: Session, user: User, recurrence_id: int, *, general: bool
) -> None:
    """Exclui a série e todas as linhas geradas (AC-119).

    `general=True` restringe ao orçamento sem cartão; `False`, às
    séries de cartão. Séries de outro escopo ou de outro usuário
    retornam 404.
    """
    record = db.scalar(
        select(BudgetRecurrence).where(
            BudgetRecurrence.id == recurrence_id,
            BudgetRecurrence.user_id == user.id,
        )
    )
    scope_matches = record is not None and (
        (record.credit_card_id is None) == general
    )
    if not scope_matches:
        raise AppError(
            code="recurrence_not_found",
            message="Recorrência de orçamento não encontrada.",
            http_status=404,
        )

    # Exclusão explícita das linhas: não depende de CASCADE do banco.
    for budget_model in (CardCategoryBudget, CategoryBudget):
        db.execute(
            delete(budget_model).where(
                budget_model.recurrence_id == record.id,
                budget_model.user_id == user.id,
            )
        )
    db.delete(record)
    db.commit()


def recurrence_payload(record: BudgetRecurrence) -> dict:
    return {
        "id": record.id,
        "mode": record.mode,
        "amount": money(record.amount),
        "count": record.count,
        "start_month": month_str(record.start_month),
    }


def row_recurrences(db: Session, budgets: list) -> dict[int, dict]:
    """Mapa linha → dados da série (badge "Parcela X/Y"), vazio para
    linhas avulsas. A posição é derivada do mês inicial da série."""
    ids = {budget.recurrence_id for budget in budgets if budget.recurrence_id}
    if not ids:
        return {}
    records = {
        record.id: record
        for record in db.scalars(
            select(BudgetRecurrence).where(BudgetRecurrence.id.in_(ids))
        )
    }
    result = {}
    for budget in budgets:
        record = records.get(budget.recurrence_id) if budget.recurrence_id else None
        if record is None:
            continue
        position = (
            (budget.reference_month.year - record.start_month.year) * 12
            + (budget.reference_month.month - record.start_month.month)
            + 1
        )
        result[budget.id] = {
            "id": record.id,
            "mode": record.mode,
            "position": position,
            "total": record.count,
        }
    return result


def _conflict_months(
    db: Session,
    user: User,
    budget_model,
    category_id: int,
    months: list[date],
    credit_card_id: int | None,
) -> list[str]:
    filters = [
        budget_model.user_id == user.id,
        budget_model.category_id == category_id,
        budget_model.reference_month.in_(months),
    ]
    if credit_card_id is not None:
        filters.append(budget_model.credit_card_id == credit_card_id)
    rows = db.scalars(
        select(budget_model.reference_month).where(*filters)
    ).all()
    return sorted(month_str(item) for item in rows)
