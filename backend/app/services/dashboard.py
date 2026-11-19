from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Category,
    CreditCard,
    CreditCardInvoice,
    CreditCardPurchase,
    Transaction,
    User,
)

ZERO = Decimal("0.00")
CENTS = Decimal("0.01")


def _money(value) -> Decimal:
    """Normaliza valores monetários para duas casas decimais (spec §7.3)."""
    return Decimal(str(value if value is not None else 0)).quantize(
        CENTS, rounding=ROUND_HALF_UP
    )


def monthly_summary(db: Session, user: User, year: int, month: int) -> dict:
    """Resumo do mês (T-035), conforme a política de contabilização
    (`spec.md` §7.2): movimentações comuns contam na data do lançamento
    e faturas de cartão contam uma única vez, como despesa variável do
    mês do seu vencimento (T-049). O detalhamento de compras individuais
    não é somado novamente (AC-059).
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

    # Faturas com vencimento no mês entram como despesa variável (§7.2.4).
    card_invoices_total, card_invoice_items = _card_invoices_in_range(
        db, user, start, end
    )
    variable_expenses += card_invoices_total

    total_outflows = fixed_expenses + variable_expenses + investments

    return {
        "month": f"{year:04d}-{month:02d}",
        "total_income": _money(income),
        "total_fixed_expenses": _money(fixed_expenses),
        "total_variable_expenses": _money(variable_expenses),
        "total_investments": _money(investments),
        "total_outflows": _money(total_outflows),
        "remaining": _money(income - total_outflows),
        "card_purchases_total": _money(card_invoices_total),
        "income_items": _group_items(db, user, start, end, "income"),
        "fixed_expense_items": _group_items(db, user, start, end, "expense", "fixed"),
        "variable_expense_items": _group_items(
            db, user, start, end, "expense", "variable"
        )
        + card_invoice_items,
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

        # Mesma política do resumo mensal: faturas no mês do vencimento.
        card_invoices_total, _items = _card_invoices_in_range(db, user, start, end)
        variable_expenses += card_invoices_total

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
            "final_balance": _money(total_income - total_expenses - total_investments),
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


def _card_invoices_in_range(
    db: Session, user: User, start: date, end: date
) -> tuple[Decimal, list[dict]]:
    """Faturas de cartão com vencimento no período (competência da fatura,
    `spec.md` §7.2).

    Retorna o total consolidado e os itens "Fatura <cartão>" do grupo
    "Contas a pagar --- Variáveis". As compras individuais não são
    somadas: a fatura é contabilizada uma única vez (AC-059).
    """
    rows = db.execute(
        select(
            CreditCardInvoice.id,
            CreditCard.name,
            func.coalesce(func.sum(CreditCardPurchase.total_amount), ZERO),
        )
        .join(CreditCard, CreditCard.id == CreditCardInvoice.credit_card_id)
        .outerjoin(
            CreditCardPurchase, CreditCardPurchase.invoice_id == CreditCardInvoice.id
        )
        .where(
            CreditCardInvoice.user_id == user.id,
            CreditCardInvoice.due_date >= start,
            CreditCardInvoice.due_date < end,
        )
        .group_by(CreditCardInvoice.id, CreditCard.name)
        .order_by(CreditCardInvoice.due_date, CreditCard.name)
    ).all()

    total = ZERO
    items = []
    for _invoice_id, card_name, invoice_total in rows:
        total += invoice_total
        if invoice_total > ZERO:
            items.append(
                {"name": f"Fatura {card_name}", "total": _money(invoice_total)}
            )
    return total, items


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

        # Faturas de cartão fazem parte das despesas do mês (§7.2.4).
        card_invoices_total, _items = _card_invoices_in_range(db, user, start, end)
        expenses += card_invoices_total

        points.append(
            {
                "month": f"{point_year:04d}-{point_month:02d}",
                "income": _money(income),
                "expenses": _money(expenses),
            }
        )
    return points
