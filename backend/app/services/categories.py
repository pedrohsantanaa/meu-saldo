"""Regras de categorias (T-027/T-028)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Category, User
from app.schemas.category import CategoryCreate, CategoryUpdate

GROUP_TYPES = {"income", "expense", "investment"}
EXPENSE_TYPES = {"fixed", "variable"}


def list_categories(
    db: Session,
    user: User,
    group_type: str | None = None,
    is_active: bool | None = None,
) -> list[Category]:
    query = select(Category).where(Category.user_id == user.id)
    if group_type is not None:
        query = query.where(Category.group_type == group_type)
    if is_active is not None:
        query = query.where(Category.is_active == is_active)
    return list(db.scalars(query.order_by(Category.name)))


def create_category(db: Session, user: User, payload: CategoryCreate) -> Category:
    _validate_payload(payload.group_type, payload.expense_type)

    existing = db.scalar(
        select(Category).where(
            Category.user_id == user.id,
            Category.name == payload.name.strip(),
            Category.group_type == payload.group_type,
        )
    )
    if existing is not None:
        raise AppError(
            code="category_already_exists",
            message="Já existe uma categoria com este nome para este tipo.",
            http_status=409,
        )

    category = Category(
        user_id=user.id,
        name=payload.name.strip(),
        group_type=payload.group_type,
        expense_type=payload.expense_type,
        color=payload.color,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(
    db: Session, user: User, category_id: int, payload: CategoryUpdate
) -> Category:
    category = _get_owned(db, user, category_id)

    group_type = payload.group_type or category.group_type
    expense_type = (
        payload.expense_type
        if payload.expense_type is not None
        else category.expense_type
    )
    _validate_payload(group_type, expense_type)

    if payload.name is not None:
        name = payload.name.strip()
        duplicate = db.scalar(
            select(Category).where(
                Category.user_id == user.id,
                Category.name == name,
                Category.group_type == group_type,
                Category.id != category.id,
            )
        )
        if duplicate is not None:
            raise AppError(
                code="category_already_exists",
                message="Já existe uma categoria com este nome para este tipo.",
                http_status=409,
            )
        category.name = name

    category.group_type = group_type
    category.expense_type = expense_type
    if payload.color is not None:
        category.color = payload.color

    db.commit()
    db.refresh(category)
    return category


def set_category_active(
    db: Session, user: User, category_id: int, is_active: bool
) -> Category:
    category = _get_owned(db, user, category_id)
    category.is_active = is_active
    db.commit()
    db.refresh(category)
    return category


def _get_owned(db: Session, user: User, category_id: int) -> Category:
    category = db.scalar(
        select(Category).where(Category.id == category_id, Category.user_id == user.id)
    )
    if category is None:
        raise AppError(
            code="not_found",
            message="Categoria não encontrada.",
            http_status=404,
        )
    return category


def _validate_payload(group_type: str, expense_type: str | None) -> None:
    if group_type not in GROUP_TYPES:
        raise AppError(
            code="invalid_group_type",
            message="Tipo de categoria inválido.",
            http_status=400,
        )
    if group_type == "expense" and expense_type not in EXPENSE_TYPES:
        raise AppError(
            code="expense_type_required",
            message="Despesas exigem classificação fixa ou variável.",
            http_status=400,
        )
    if group_type != "expense" and expense_type is not None:
        raise AppError(
            code="expense_type_not_allowed",
            message="Apenas despesas possuem classificação fixa ou variável.",
            http_status=400,
        )
