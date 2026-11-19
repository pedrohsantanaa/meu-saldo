"""Compras no cartão de crédito (T-047).

Regras (`spec.md` §6.9): a compra é associada a um cartão ativo do
usuário (AC-054), com categoria de despesa ativa e valor > 0. Cada
compra é atribuída à fatura do seu ciclo no registro (AC-053/AC-055) e
contabilizada uma única vez, pela fatura (`spec.md` §7.2). Edições e
exclusões recalculam a fatura e o limite (AC-057).

Sem parcelamento no MVP (T-005): `installments_count` é fixo em 1 e a
interface não oferece parcelamento (AC-061).
"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import CreditCardPurchase, User
from app.schemas.credit_card_purchase import PurchaseCreate, PurchaseUpdate
from app.services import invoices as invoices_service
from app.services.cards import get_owned_card, get_owned_category


def list_purchases(
    db: Session,
    user: User,
    card_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[CreditCardPurchase]:
    get_owned_card(db, user, card_id)
    query = select(CreditCardPurchase).where(
        CreditCardPurchase.user_id == user.id,
        CreditCardPurchase.credit_card_id == card_id,
    )
    if date_from is not None:
        query = query.where(CreditCardPurchase.purchase_date >= date_from)
    if date_to is not None:
        query = query.where(CreditCardPurchase.purchase_date <= date_to)
    return list(
        db.scalars(
            query.order_by(
                CreditCardPurchase.purchase_date.desc(), CreditCardPurchase.id.desc()
            )
        )
    )


def get_purchase(
    db: Session, user: User, card_id: int, purchase_id: int
) -> CreditCardPurchase:
    return _get_owned_purchase(db, user, card_id, purchase_id)


def create_purchase(
    db: Session, user: User, card_id: int, payload: PurchaseCreate
) -> CreditCardPurchase:
    card = get_owned_card(db, user, card_id)
    if not card.is_active:
        raise AppError(
            code="inactive_card",
            message="Cartão inativo não aceita novas compras.",
            http_status=400,
        )
    category = _validate_category(db, user, payload.category_id)

    invoice = invoices_service.get_or_create_invoice(
        db, user, card, payload.purchase_date
    )
    purchase = CreditCardPurchase(
        user_id=user.id,
        credit_card_id=card.id,
        category_id=category.id,
        invoice_id=invoice.id,
        description=payload.description.strip(),
        purchase_date=payload.purchase_date,
        total_amount=payload.total_amount,
        installments_count=1,
        notes=payload.notes,
    )
    db.add(purchase)
    db.flush()
    invoices_service.sync_status(db, invoice)
    db.commit()
    db.refresh(purchase)
    return purchase


def update_purchase(
    db: Session,
    user: User,
    card_id: int,
    purchase_id: int,
    payload: PurchaseUpdate,
) -> CreditCardPurchase:
    purchase = _get_owned_purchase(db, user, card_id, purchase_id)
    card = get_owned_card(db, user, card_id)
    old_invoice_id = purchase.invoice_id

    if payload.category_id is not None:
        category = _validate_category(db, user, payload.category_id)
        purchase.category_id = category.id
    if payload.description is not None:
        purchase.description = payload.description.strip()
    if payload.total_amount is not None:
        purchase.total_amount = payload.total_amount
    if payload.notes is not None:
        purchase.notes = payload.notes

    if payload.purchase_date is not None and (
        payload.purchase_date != purchase.purchase_date
    ):
        # Data mudou: reatribui a compra ao ciclo da nova data.
        invoice = invoices_service.get_or_create_invoice(
            db, user, card, payload.purchase_date
        )
        purchase.invoice_id = invoice.id
        purchase.purchase_date = payload.purchase_date

    # Flush para as consultas de fatura enxergarem as mudanças pendentes
    # (a sessão de testes usa autoflush=False).
    db.flush()
    if purchase.invoice_id != old_invoice_id:
        old_invoice = invoices_service.get_owned_invoice(
            db, user, card_id, old_invoice_id
        )
        invoices_service.sync_status(db, old_invoice)
        invoices_service.prune_invoice_if_empty(db, old_invoice)
    invoices_service.sync_status(
        db,
        invoices_service.get_owned_invoice(db, user, card_id, purchase.invoice_id),
    )
    db.commit()
    db.refresh(purchase)
    return purchase


def delete_purchase(db: Session, user: User, card_id: int, purchase_id: int) -> None:
    purchase = _get_owned_purchase(db, user, card_id, purchase_id)
    invoice = invoices_service.get_owned_invoice(db, user, card_id, purchase.invoice_id)
    db.delete(purchase)
    db.flush()
    invoices_service.sync_status(db, invoice)
    invoices_service.prune_invoice_if_empty(db, invoice)
    db.commit()


def _get_owned_purchase(
    db: Session, user: User, card_id: int, purchase_id: int
) -> CreditCardPurchase:
    purchase = db.scalar(
        select(CreditCardPurchase).where(
            CreditCardPurchase.id == purchase_id,
            CreditCardPurchase.credit_card_id == card_id,
            CreditCardPurchase.user_id == user.id,
        )
    )
    if purchase is None:
        raise AppError(
            code="purchase_not_found",
            message="Compra não encontrada.",
            http_status=404,
        )
    return purchase


def _validate_category(db: Session, user: User, category_id: int):
    """Categoria de despesa, ativa e do usuário (compatível com a compra)."""
    category = get_owned_category(db, user, category_id)
    if not category.is_active:
        raise AppError(
            code="inactive_category",
            message="A categoria está inativa. Reative-a ou escolha outra categoria.",
            http_status=400,
        )
    if category.group_type != "expense":
        raise AppError(
            code="category_type_mismatch",
            message=("A categoria escolhida não é compatível com compras no cartão."),
            http_status=400,
        )
    return category
