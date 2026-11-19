"""Ciclo de fatura do cartão de crédito (T-048).

Regras aprovadas em T-004 (`spec.md` §6.10) e política de
contabilização de T-002 (`spec.md` §7.2):

- o ciclo é considerado encerrado no início do dia do fechamento:
  compras realizadas exatamente no dia do fechamento entram no ciclo
  seguinte (AC-103);
- compras após o fechamento pertencem ao ciclo seguinte (AC-102);
- dia de fechamento ou vencimento inexistente no mês usa o último dia do
  mês correspondente (AC-104);
- a primeira fatura de um cartão começa na data de cadastro e vai até o
  dia anterior ao primeiro fechamento posterior ao cadastro (AC-105);
- a fatura é identificada pelo mês do seu vencimento: a "fatura de
  janeiro" é a que vence em janeiro (AC-101). O vencimento é a primeira
  ocorrência do dia de vencimento estritamente posterior ao fechamento.

Funções puras, sem acesso a banco: recebem apenas `closing_day`,
`due_day` e datas. A atribuição de uma compra à fatura é feita uma única
vez, no registro da compra (snapshot); mudanças posteriores no dia de
fechamento do cartão não movem compras já registradas.
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class InvoiceCycle:
    """Ciclo de fatura resolvido para uma data de compra."""

    reference_month: date  # primeiro dia do mês do vencimento
    closing_date: date  # fechamento do ciclo (compras até a véspera)
    due_date: date  # vencimento da fatura


def _last_day(year: int, month: int) -> int:
    if month == 12:
        return (date(year + 1, 1, 1) - date(year, 12, 1)).days
    return (date(year, month + 1, 1) - date(year, month, 1)).days


def _effective_day(year: int, month: int, day: int) -> date:
    """Dia configurado no mês; se não existir, usa o último dia (AC-104)."""
    return date(year, month, min(day, _last_day(year, month)))


def _next_month(year: int, month: int) -> tuple[int, int]:
    return (year + 1, 1) if month == 12 else (year, month + 1)


def _first_day_after(day: int, ref: date) -> date:
    """Primeira ocorrência do dia `day` (com ajuste de mês curto)
    estritamente posterior a `ref`."""
    year, month = ref.year, ref.month
    candidate = _effective_day(year, month, day)
    if candidate > ref:
        return candidate
    year, month = _next_month(year, month)
    return _effective_day(year, month, day)


def closing_after(closing_day: int, ref: date) -> date:
    """Data de fechamento do ciclo que contém `ref` (fechamento > ref)."""
    return _first_day_after(closing_day, ref)


def due_after(due_day: int, closing_date: date) -> date:
    """Vencimento da fatura que fecha em `closing_date`."""
    return _first_day_after(due_day, closing_date)


def resolve_invoice_cycle(
    closing_day: int,
    due_day: int,
    purchase_date: date,
    card_start: date,
) -> InvoiceCycle:
    """Resolve o ciclo da fatura de uma compra.

    `card_start` é a data de cadastro do cartão: compras anteriores ao
    cadastro (registro retroativo) são alocadas à primeira fatura, cujo
    ciclo começa no cadastro (AC-105). Compras exatamente no dia do
    fechamento caem no ciclo seguinte (AC-103).
    """
    ref = max(purchase_date, card_start)
    closing_date = closing_after(closing_day, ref)
    due_date = due_after(due_day, closing_date)
    return InvoiceCycle(
        reference_month=date(due_date.year, due_date.month, 1),
        closing_date=closing_date,
        due_date=due_date,
    )
