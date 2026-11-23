from decimal import Decimal
from typing import Literal

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


class BudgetRecurrenceCreate(BaseModel):
    """Recorrência de orçamento (T-075, `spec.md` §6.13).

    - `installments`: `amount` é o valor TOTAL, dividido em `count`
      parcelas mensais com soma exata (a última parcela absorve os
      centavos, `spec.md` §7.3);
    - `monthly`: `amount` é o valor MENSAL, repetido por `count` meses.

    O mês inicial é o `month` da requisição e o horizonte é sempre fixo
    (2 a 60 meses, sem repetição indefinida).
    """

    mode: Literal["installments", "monthly"]
    amount: Decimal = Field(gt=0, decimal_places=2, max_digits=12)
    count: int = Field(ge=2, le=60)


class BudgetSeriesCreate(BaseModel):
    """Criação de série de orçamentos sem cartão (T-075)."""

    category_id: int
    month: str = Field(pattern=MONTH_PATTERN)
    recurrence: BudgetRecurrenceCreate


class BudgetSeriesCreateCard(BudgetSeriesCreate):
    """Criação de série de orçamentos por cartão (T-075)."""

    card_id: int


class BudgetRowRecurrence(BaseModel):
    """Identificação da série na linha do orçamento (badge)."""

    id: int
    mode: str
    position: int
    total: int


class BudgetRecurrenceInfo(BaseModel):
    id: int
    mode: str
    amount: Decimal
    count: int
    start_month: str


class BudgetCreateGeneral(BaseModel):
    """Orçamento mensal por categoria, sem cartão (despesas fixas e
    variáveis lançadas fora do cartão).

    A combinação usuário + categoria + mês é única (`spec.md` §6.13);
    valores não negativos (mesma regra do orçamento por cartão, T-055).
    """

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
    recurrence: BudgetRowRecurrence | None = None


class BudgetRecurrenceCreated(BaseModel):
    """Resultado da criação de uma série (AC-116, AC-117)."""

    recurrence: BudgetRecurrenceInfo
    months: list[str]
    rows: list[BudgetRow]


class BudgetTotals(BaseModel):
    budget_amount: Decimal
    spent: Decimal
    remaining: Decimal


class BudgetSummary(BaseModel):
    month: str
    card_id: int
    rows: list[BudgetRow]
    totals: BudgetTotals


class BudgetSummaryGeneral(BaseModel):
    """Resumo do orçamento sem cartão: mesmas linhas e totalizadores do
    orçamento por cartão, sem `card_id`."""

    month: str
    rows: list[BudgetRow]
    totals: BudgetTotals
