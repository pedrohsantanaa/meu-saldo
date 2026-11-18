from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Category, User
from app.schemas.category import (
    CategoryCreate,
    CategoryRead,
    CategoryStatusUpdate,
    CategoryUpdate,
)
from app.services import categories as categories_service

router = APIRouter(prefix="/categories", tags=["categorias"])


@router.get("", response_model=list[CategoryRead])
def list_categories(
    group_type: str | None = None,
    is_active: bool | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Category]:
    return categories_service.list_categories(db, current_user, group_type, is_active)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Category:
    return categories_service.create_category(db, current_user, payload)


@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Category:
    return categories_service.update_category(db, current_user, category_id, payload)


@router.patch("/{category_id}/status", response_model=CategoryRead)
def set_category_status(
    category_id: int,
    payload: CategoryStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Category:
    return categories_service.set_category_active(
        db, current_user, category_id, payload.is_active
    )
