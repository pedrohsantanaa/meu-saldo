from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Category, Transaction, User

ZERO = Decimal("0.00")
CENTS = Decimal("0.01")


def _money(value) -> Decimal:
    """Normaliza valores monetários para duas casas decimais (spec §7.3)."""
    return Decimal(str(value if value is not None else 0)).quantize(
        CENTS, rounding=ROUND_HALF_UP
    )


def monthly_summary(db: Session, user: User, year: int, month: int) -> dict:
    """Resumo do mês (T-035), conforme a política de contabilização
    (`spec.md` §7.2): movimentações comuns contam na data do lançamento.

    Compras no cartão entram pelo ciclo da fatura na Fase 6; até lá o
    total de compras no cartão é zero e não há risco de duplicidade
    com faturas (T-039).
    """
    start, end = _month_bounds(year, month)

    income = ZERO
    fixed_expenses = ZERO
    variable_expenses = ZERO
    investments = ZERO

    for movement_type, expense_type, total in _sums_in_range(db, user, start, end):
        if movement_type == "income":
            income += total
        elif movement_type == "investment":
            investments += total
        elif expense_type == "fixed":
            fixed_expenses += total
        else:
            variable_expenses += total

    total_outflows = fixed_expenses + variable_expenses + investments

    return {
        "month": f"{year:04d}-{month:02d}",
        "total_income": _money(income),
        "total_fixed_expenses": _money(fixed_expenses),
        "total_variable_expenses": _money(variable_expenses),
        "total_investments": _money(investments),
        "total_outflows": _money(total_outflows),
        "remaining": _money(income - total_outflows),
        "card_purchases_total": _money(ZERO),
        "income_items": _group_items(db, user, start, end, "income"),
        "fixed_expense_items": _group_items(db, user, start, end, "expense", "fixed"),
        "variable_expense_items": _group_items(
            db, user, start, end, "expense", "variable"
        ),
        "investments_items": _group_items(db, user, start, end, "investment"),
        "recent_transactions": list(
            db.scalars(
                select(Transaction)
                .where(
                    Transaction.user_id == user.id,
                    Transaction.transaction_date >= start,
                    Transaction.transaction_date < end,
                )
                .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
                .limit(5)
            )
        ),
        "expenses_by_category": _group_items(db, user, start, end, "expense"),
        "trend": _trend(db, user, year, month),
    }


def annual_summary(db: Session, user: User, year: int) -> dict:
    """Resumo anual (T-039): 12 meses em ordem cronológica, inclusive os
    meses sem movimentação.
    """
    months = []
    total_income = ZERO
    total_expenses = ZERO
    total_investments = ZERO

    for month in range(1, 13):
        start, end = _month_bounds(year, month)
        income = ZERO
        fixed_expenses = ZERO
        variable_expenses = ZERO
        investments = ZERO

        for movement_type, expense_type, total in _sums_in_range(db, user, start, end):
            if movement_type == "income":
                income += total
            elif movement_type == "investment":
                investments += total
            elif expense_type == "fixed":
                fixed_expenses += total
            else:
                variable_expenses += total

        remaining = income - (fixed_expenses + variable_expenses + investments)
        months.append(
            {
                "month": f"{year:04d}-{month:02d}",
                "total_income": _money(income),
                "total_fixed_expenses": _money(fixed_expenses),
                "total_variable_expenses": _money(variable_expenses),
                "total_investments": _money(investments),
                "remaining": _money(remaining),
            }
        )
        total_income += income
        total_expenses += fixed_expenses + variable_expenses
        total_investments += investments

    return {
        "year": year,
        "months": months,
        "totals": {
            "total_income": _money(total_income),
            "total_expenses": _money(total_expenses),
            "total_investments": _money(total_investments),
            "final_balance": _money(
                total_income - total_expenses - total_investments
            ),
        },
    }


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)
    return start, end


def _sums_in_range(db: Session, user: User, start: date, end: date):
    return db.execute(
        select(
            Transaction.type,
            Transaction.expense_type,
            func.sum(Transaction.amount),
        )
        .where(
            Transaction.user_id == user.id,
            Transaction.transaction_date >= start,
            Transaction.transaction_date < end,
        )
        .group_by(Transaction.type, Transaction.expense_type)
    ).all()


def _group_items(
    db: Session,
    user: User,
    start: date,
    end: date,
    movement_type: str,
    expense_type: str | None = None,
) -> list[dict]:
    query = (
        select(Category.name, func.sum(Transaction.amount))
        .join(Transaction, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user.id,
            Transaction.type == movement_type,
            Transaction.transaction_date >= start,
            Transaction.transaction_date < end,
        )
        .group_by(Category.name)
        .order_by(Category.name)
    )
    if expense_type is not None:
        query = query.where(Transaction.expense_type == expense_type)

    return [{"name": name, "total": _money(total)} for name, total in db.execute(query)]


def _trend(db: Session, user: User, year: int, month: int) -> list[dict]:
    """Últimos 6 meses (inclusive o mês consultado) para o gráfico."""
    points = []
    for offset in range(5, -1, -1):
        total_month = month - offset
        point_year = year + (total_month - 1) // 12
        point_month = (total_month - 1) % 12 + 1
        start, end = _month_bounds(point_year, point_month)

        income = ZERO
        expenses = ZERO
        for movement_type, _expense_type, total in _sums_in_range(db, user, start, end):
            if movement_type == "income":
                income += total
            elif movement_type == "expense":
                expenses += total

        points.append(
            {
                "month": f"{point_year:04d}-{point_month:02d}",
                "income": _money(income),
                "expenses": _money(expenses),
            }
        )
    return points
