from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

MovementType = Literal["income", "expense", "investment"]
ExpenseType = Literal["fixed", "variable"]
PaymentMethod = Literal["dinheiro", "pix", "debito", "outra"]


class TransactionCreate(BaseModel):
    type: MovementType
    description: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0, decimal_places=2, max_digits=12)
    transaction_date: date
    category_id: int
    expense_type: ExpenseType | None = None
    payment_method: PaymentMethod | None = None
    notes: str | None = Field(default=None, max_length=500)


class TransactionUpdate(BaseModel):
    type: MovementType | None = None
    description: str | None = Field(default=None, min_length=1, max_length=200)
    amount: Decimal | None = Field(default=None, gt=0, decimal_places=2, max_digits=12)
    transaction_date: date | None = None
    category_id: int | None = None
    expense_type: ExpenseType | None = None
    payment_method: PaymentMethod | None = None
    notes: str | None = Field(default=None, max_length=500)


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    description: str
    amount: Decimal
    transaction_date: date
    category_id: int
    expense_type: str | None
    payment_method: str | None
    notes: str | None
    created_at: datetime
