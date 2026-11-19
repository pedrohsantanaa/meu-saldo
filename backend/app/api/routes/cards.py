from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import (
    CreditCardInvoicePayment,
    CreditCardPurchase,
    User,
)
from app.schemas.credit_card import (
    CardCreate,
    CardRead,
    CardStatusUpdate,
    CardUpdate,
)
from app.schemas.credit_card_invoice import (
    InvoiceDetail,
    InvoiceOverview,
    InvoiceRead,
    PaymentCreate,
    PaymentRead,
)
from app.schemas.credit_card_purchase import (
    PurchaseCreate,
    PurchaseRead,
    PurchaseUpdate,
)
from app.services import card_purchases as purchases_service
from app.services import cards as cards_service
from app.services import invoices as invoices_service

router = APIRouter(prefix="/cards", tags=["cartões"])


@router.get("", response_model=list[CardRead])
def list_cards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    return cards_service.list_cards(db, current_user)


@router.post("", response_model=CardRead, status_code=status.HTTP_201_CREATED)
def create_card(
    payload: CardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return cards_service.create_card(db, current_user, payload)


@router.get("/{card_id}", response_model=CardRead)
def get_card(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return cards_service.get_card(db, current_user, card_id)


@router.put("/{card_id}", response_model=CardRead)
def update_card(
    card_id: int,
    payload: CardUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return cards_service.update_card(db, current_user, card_id, payload)


@router.patch("/{card_id}/status", response_model=CardRead)
def set_card_status(
    card_id: int,
    payload: CardStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return cards_service.set_card_status(db, current_user, card_id, payload.is_active)


@router.get("/{card_id}/purchases", response_model=list[PurchaseRead])
def list_purchases(
    card_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CreditCardPurchase]:
    return purchases_service.list_purchases(
        db, current_user, card_id, date_from=date_from, date_to=date_to
    )


@router.post(
    "/{card_id}/purchases",
    response_model=PurchaseRead,
    status_code=status.HTTP_201_CREATED,
)
def create_purchase(
    card_id: int,
    payload: PurchaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CreditCardPurchase:
    return purchases_service.create_purchase(db, current_user, card_id, payload)


@router.get("/{card_id}/purchases/{purchase_id}", response_model=PurchaseRead)
def get_purchase(
    card_id: int,
    purchase_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CreditCardPurchase:
    return purchases_service.get_purchase(db, current_user, card_id, purchase_id)


@router.put("/{card_id}/purchases/{purchase_id}", response_model=PurchaseRead)
def update_purchase(
    card_id: int,
    purchase_id: int,
    payload: PurchaseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CreditCardPurchase:
    return purchases_service.update_purchase(
        db, current_user, card_id, purchase_id, payload
    )


@router.delete(
    "/{card_id}/purchases/{purchase_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_purchase(
    card_id: int,
    purchase_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    purchases_service.delete_purchase(db, current_user, card_id, purchase_id)


@router.get("/{card_id}/invoices", response_model=list[InvoiceRead])
def list_invoices(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    return invoices_service.list_invoices(db, current_user, card_id)


@router.get("/{card_id}/invoices/overview", response_model=InvoiceOverview)
def invoice_overview(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    card = cards_service.get_owned_card(db, current_user, card_id)
    return invoices_service.overview(db, current_user, card)


@router.get("/{card_id}/invoices/{invoice_id}", response_model=InvoiceDetail)
def get_invoice(
    card_id: int,
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return invoices_service.invoice_detail_payload(
        db, current_user, card_id, invoice_id
    )


@router.post(
    "/{card_id}/invoices/{invoice_id}/payments",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
)
def register_payment(
    card_id: int,
    invoice_id: int,
    payload: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CreditCardInvoicePayment:
    return invoices_service.register_payment(
        db, current_user, card_id, invoice_id, payload
    )
