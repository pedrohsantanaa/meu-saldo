from decimal import Decimal

from pydantic import BaseModel, Field

MONTH_PATTERN = r"^\d{4}-\d{2}$"


class BudgetCreate(BaseModel):
    """Orçamento mensal por categoria e cartão (T-055).

    A combinação usuário + cartão + categoria + mês é única
    (`spec.md` §6.13); valores não negativos (T-055).
    """

    card_id: int
    category_id: int
    month: str = Field(pattern=MONTH_PATTERN)
    budget_amount: Decimal = Field(ge=0, decimal_places=2, max_digits=12)


class BudgetUpdate(BaseModel):
    budget_amount: Decimal = Field(ge=0, decimal_places=2, max_digits=12)


class BudgetRow(BaseModel):
    """Linha do orçamento (T-054).

    `budget_amount` nulo indica categoria sem orçamento ("Não definido",
    AC-072): o restante e o percentual não são calculados, sem assumir
    zero. `usage_percent` só existe para orçamento maior que zero
    (T-058).
    """

    id: int | None
    category_id: int
    category_name: str
    budget_amount: Decimal | None
    spent: Decimal
    remaining: Decimal | None
    usage_percent: float | None


class BudgetTotals(BaseModel):
    budget_amount: Decimal
    spent: Decimal
    remaining: Decimal


class BudgetSummary(BaseModel):
    month: str
    card_id: int
    rows: list[BudgetRow]
    totals: BudgetTotals
