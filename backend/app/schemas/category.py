from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

GroupType = Literal["income", "expense", "investment"]
ExpenseType = Literal["fixed", "variable"]


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    group_type: GroupType
    expense_type: ExpenseType | None = None
    color: str | None = Field(default=None, max_length=20)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    group_type: GroupType | None = None
    expense_type: ExpenseType | None = None
    color: str | None = Field(default=None, max_length=20)


class CategoryStatusUpdate(BaseModel):
    is_active: bool


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    group_type: str
    expense_type: str | None
    color: str | None
    is_active: bool
    is_default: bool
