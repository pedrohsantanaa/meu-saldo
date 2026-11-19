from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.credit_card_purchase import PurchaseRead


class InvoiceRead(BaseModel):
    """Fatura do cartão (T-049) com totais derivados das compras."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    credit_card_id: int
    reference_month: date
    closing_date: date
    due_date: date
    status: str
    total: Decimal
    paid_amount: Decimal
    open_amount: Decimal


class PaymentCreate(BaseModel):
    """Pagamento (liquidação) de fatura (T-051).

    Total ou parcial; nunca gera despesa de consumo (AC-060).
    """

    amount: Decimal = Field(gt=0, decimal_places=2, max_digits=12)
    paid_at: date | None = None


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    amount: Decimal
    paid_at: date
    created_at: datetime


class InvoiceDetail(InvoiceRead):
    purchases: list[PurchaseRead]
    payments: list[PaymentRead]


class InvoiceOverview(BaseModel):
    """Fatura atual e próxima fatura do cartão (AC-052)."""

    current: InvoiceRead | None
    next: InvoiceRead | None
