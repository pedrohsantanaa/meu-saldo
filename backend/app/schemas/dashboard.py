from decimal import Decimal

from pydantic import BaseModel

from app.schemas.transaction import TransactionRead


class GroupItem(BaseModel):
    name: str
    total: Decimal


class TrendPoint(BaseModel):
    month: str
    income: Decimal
    expenses: Decimal


class MonthlySummary(BaseModel):
    month: str
    total_income: Decimal
    total_fixed_expenses: Decimal
    total_variable_expenses: Decimal
    total_investments: Decimal
    total_outflows: Decimal
    remaining: Decimal
    card_purchases_total: Decimal
    income_items: list[GroupItem]
    fixed_expense_items: list[GroupItem]
    variable_expense_items: list[GroupItem]
    investments_items: list[GroupItem]
    recent_transactions: list[TransactionRead]
    expenses_by_category: list[GroupItem]
    trend: list[TrendPoint]


class AnnualMonth(BaseModel):
    month: str
    total_income: Decimal
    total_fixed_expenses: Decimal
    total_variable_expenses: Decimal
    total_investments: Decimal
    remaining: Decimal


class AnnualTotals(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    total_investments: Decimal
    final_balance: Decimal


class AnnualSummary(BaseModel):
    year: int
    months: list[AnnualMonth]
    totals: AnnualTotals
