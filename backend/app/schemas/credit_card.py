from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CardStatus = Literal["open", "partial", "paid"]


class CardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    issuer: str | None = Field(default=None, max_length=80)
    credit_limit: Decimal = Field(ge=0, decimal_places=2, max_digits=12)
    closing_day: int = Field(ge=1, le=31)
    due_day: int = Field(ge=1, le=31)


class CardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    issuer: str | None = Field(default=None, max_length=80)
    credit_limit: Decimal | None = Field(
        default=None, ge=0, decimal_places=2, max_digits=12
    )
    closing_day: int | None = Field(default=None, ge=1, le=31)
    due_day: int | None = Field(default=None, ge=1, le=31)


class CardStatusUpdate(BaseModel):
    is_active: bool


class CardRead(BaseModel):
    """Cartão com os indicadores de limite (T-050, `spec.md` §6.11).

    `committed_amount` = compras em faturas não pagas deduzidas dos
    pagamentos registrados; `available_limit` = limite total −
    comprometido.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    issuer: str | None
    credit_limit: Decimal
    closing_day: int
    due_day: int
    is_active: bool
    committed_amount: Decimal
    available_limit: Decimal
    created_at: datetime
