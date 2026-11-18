from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Transaction, User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)
from app.services import transactions as transactions_service

router = APIRouter(prefix="/transactions", tags=["movimentações"])


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    date_from: date | None = None,
    date_to: date | None = None,
    type: str | None = None,
    category_id: int | None = None,
    payment_method: str | None = None,
    search: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Transaction]:
    return transactions_service.list_transactions(
        db,
        current_user,
        date_from=date_from,
        date_to=date_to,
        movement_type=type,
        category_id=category_id,
        payment_method=payment_method,
        search=search,
    )


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Transaction:
    return transactions_service.create_transaction(db, current_user, payload)


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Transaction:
    return transactions_service.get_transaction(db, current_user, transaction_id)


@router.put("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Transaction:
    return transactions_service.update_transaction(
        db, current_user, transaction_id, payload
    )


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    transactions_service.delete_transaction(db, current_user, transaction_id)
