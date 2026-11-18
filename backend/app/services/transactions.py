"""Regras de movimentações financeiras (T-029 a T-033)."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Category, Transaction, User
from app.schemas.transaction import TransactionCreate, TransactionUpdate

TYPE_TO_GROUP = {"income": "income", "expense": "expense", "investment": "investment"}
PAYMENT_METHODS = {"dinheiro", "pix", "debito", "outra"}


def list_transactions(
    db: Session,
    user: User,
    date_from: date | None = None,
    date_to: date | None = None,
    movement_type: str | None = None,
    category_id: int | None = None,
    payment_method: str | None = None,
    search: str | None = None,
) -> list[Transaction]:
    query = select(Transaction).where(Transaction.user_id == user.id)
    if date_from is not None:
        query = query.where(Transaction.transaction_date >= date_from)
    if date_to is not None:
        query = query.where(Transaction.transaction_date <= date_to)
    if movement_type is not None:
        query = query.where(Transaction.type == movement_type)
    if category_id is not None:
        query = query.where(Transaction.category_id == category_id)
    if payment_method is not None:
        query = query.where(Transaction.payment_method == payment_method)
    if search:
        query = query.where(Transaction.description.ilike(f"%{search}%"))

    return list(
        db.scalars(
            query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        )
    )


def get_transaction(db: Session, user: User, transaction_id: int) -> Transaction:
    return _get_owned(db, user, transaction_id)


def create_transaction(
    db: Session, user: User, payload: TransactionCreate
) -> Transaction:
    category = _get_owned_category(db, user, payload.category_id)
    _validate_movement(
        payload.type, payload.expense_type, payload.payment_method, category
    )

    transaction = Transaction(
        user_id=user.id,
        category_id=category.id,
        type=payload.type,
        expense_type=payload.expense_type,
        description=payload.description.strip(),
        amount=payload.amount,
        transaction_date=payload.transaction_date,
        payment_method=payload.payment_method,
        notes=payload.notes,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def update_transaction(
    db: Session, user: User, transaction_id: int, payload: TransactionUpdate
) -> Transaction:
    transaction = _get_owned(db, user, transaction_id)

    movement_type = payload.type or transaction.type
    category_id = payload.category_id or transaction.category_id
    expense_type = (
        payload.expense_type
        if payload.expense_type is not None
        else transaction.expense_type
    )
    payment_method = (
        payload.payment_method
        if payload.payment_method is not None
        else transaction.payment_method
    )

    category = _get_owned_category(db, user, category_id)
    _validate_movement(movement_type, expense_type, payment_method, category)

    transaction.type = movement_type
    transaction.category_id = category.id
    transaction.expense_type = expense_type
    transaction.payment_method = payment_method
    if payload.description is not None:
        transaction.description = payload.description.strip()
    if payload.amount is not None:
        transaction.amount = payload.amount
    if payload.transaction_date is not None:
        transaction.transaction_date = payload.transaction_date
    if payload.notes is not None:
        transaction.notes = payload.notes

    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, user: User, transaction_id: int) -> None:
    transaction = _get_owned(db, user, transaction_id)
    db.delete(transaction)
    db.commit()


def _get_owned(db: Session, user: User, transaction_id: int) -> Transaction:
    transaction = db.scalar(
        select(Transaction).where(
            Transaction.id == transaction_id, Transaction.user_id == user.id
        )
    )
    if transaction is None:
        raise AppError(
            code="not_found",
            message="Movimentação não encontrada.",
            http_status=404,
        )
    return transaction


def _get_owned_category(db: Session, user: User, category_id: int) -> Category:
    category = db.scalar(
        select(Category).where(Category.id == category_id, Category.user_id == user.id)
    )
    if category is None:
        raise AppError(
            code="category_not_found",
            message="Categoria não encontrada.",
            http_status=400,
        )
    return category


def _validate_movement(
    movement_type: str,
    expense_type: str | None,
    payment_method: str | None,
    category: Category,
) -> None:
    if not category.is_active:
        raise AppError(
            code="inactive_category",
            message="A categoria está inativa. Reative-a ou escolha outra categoria.",
            http_status=400,
        )

    # Impede incompatibilidade entre categoria e tipo de movimentação (AC-012).
    if category.group_type != TYPE_TO_GROUP[movement_type]:
        raise AppError(
            code="category_type_mismatch",
            message=(
                "A categoria escolhida não é compatível com o tipo "
                "da movimentação."
            ),
            http_status=400,
        )

    if movement_type == "expense":
        if expense_type is None:
            raise AppError(
                code="expense_type_required",
                message="Despesas exigem classificação fixa ou variável.",
                http_status=400,
            )
        if payment_method is None:
            raise AppError(
                code="payment_method_required",
                message="Despesas exigem forma de pagamento.",
                http_status=400,
            )
        if payment_method not in PAYMENT_METHODS:
            raise AppError(
                code="invalid_payment_method",
                message="Forma de pagamento inválida.",
                http_status=400,
            )
    elif expense_type is not None:
        raise AppError(
            code="expense_type_not_allowed",
            message="Apenas despesas possuem classificação fixa ou variável.",
            http_status=400,
        )
