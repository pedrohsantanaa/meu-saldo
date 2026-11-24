"""Movimentações unificadas: transações comuns + compras no cartão.

A listagem da tela de Movimentações reúne os dois tipos de lançamento,
identificados por `source`, sem nunca transformar uma compra no cartão
em movimentação comum (`spec.md` §7.2). Cada tipo preserva as suas
particularidades: a compra é sempre despesa, pertence a um cartão e é
consolidada na fatura indicada por `invoice_reference_month`.
"""

from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class MovementBase(BaseModel):
    """Campos comuns a qualquer lançamento da listagem unificada.

    `transaction_date` é a data da movimentação ou a data da compra.
    """

    id: int
    transaction_date: date
    description: str
    amount: Decimal
    category_id: int
    notes: str | None = None


class TransactionMovement(MovementBase):
    """Movimentação comum (receita, despesa ou investimento)."""

    source: Literal["transaction"] = "transaction"
    type: Literal["income", "expense", "investment"]
    expense_type: Literal["fixed", "variable"] | None = None
    payment_method: Literal["dinheiro", "pix", "debito", "outra"] | None = None


class CardPurchaseMovement(MovementBase):
    """Compra no cartão de crédito (particularidades preservadas).

    Sempre despesa, sempre no cartão indicado e identificada pela fatura
    em que consolida (`invoice_reference_month`, formato AAAA-MM).
    """

    source: Literal["card_purchase"] = "card_purchase"
    type: Literal["expense"] = "expense"
    expense_type: Literal["fixed", "variable"] | None = None
    credit_card_id: int
    card_name: str
    invoice_reference_month: str | None = None


MovementRow = Annotated[
    TransactionMovement | CardPurchaseMovement,
    Field(discriminator="source"),
]
