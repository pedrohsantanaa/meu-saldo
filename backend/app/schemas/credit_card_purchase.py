from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PurchaseCreate(BaseModel):
    """Compra à vista no cartão (T-047).

    Sem parcelamento no MVP (T-005, AC-061): `installments_count` não é
    aceito e permanece fixo em 1.
    """

    description: str = Field(min_length=1, max_length=200)
    total_amount: Decimal = Field(gt=0, decimal_places=2, max_digits=12)
    purchase_date: date
    category_id: int
    notes: str | None = Field(default=None, max_length=500)


class PurchaseUpdate(BaseModel):
    description: str | None = Field(default=None, min_length=1, max_length=200)
    total_amount: Decimal | None = Field(
        default=None, gt=0, decimal_places=2, max_digits=12
    )
    purchase_date: date | None = None
    category_id: int | None = None
    notes: str | None = Field(default=None, max_length=500)


class PurchaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    credit_card_id: int
    category_id: int
    invoice_id: int
    description: str
    purchase_date: date
    total_amount: Decimal
    installments_count: int
    notes: str | None
    created_at: datetime
