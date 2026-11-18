from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas.dashboard import AnnualSummary, MonthlySummary
from app.services import dashboard as dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/monthly", response_model=MonthlySummary)
def monthly_summary(
    month: str = Query(pattern=r"^\d{4}-\d{2}$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MonthlySummary:
    year, month_number = (int(part) for part in month.split("-"))
    return dashboard_service.monthly_summary(db, current_user, year, month_number)


@router.get("/annual", response_model=AnnualSummary)
def annual_summary(
    year: int = Query(ge=2000, le=2100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnnualSummary:
    return dashboard_service.annual_summary(db, current_user, year)
