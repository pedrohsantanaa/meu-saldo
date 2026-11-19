from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.budget import (
    MONTH_PATTERN,
    BudgetCreate,
    BudgetRow,
    BudgetSummary,
    BudgetUpdate,
)
from app.services import budgets as budgets_service

router = APIRouter(prefix="/budgets", tags=["orçamentos"])


@router.get("", response_model=BudgetSummary)
def list_budgets(
    month: str = Query(pattern=MONTH_PATTERN),
    card_id: int = Query(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return budgets_service.summary(db, current_user, card_id, month)


@router.post("", response_model=BudgetRow, status_code=status.HTTP_201_CREATED)
def create_budget(
    payload: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return budgets_service.create_budget(db, current_user, payload)


@router.put("/{budget_id}", response_model=BudgetRow)
def update_budget(
    budget_id: int,
    payload: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return budgets_service.update_budget(db, current_user, budget_id, payload)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    budgets_service.delete_budget(db, current_user, budget_id)
