"""Cartões de crédito do usuário (T-045).

Regras (`spec.md` §6.8): nome obrigatório; limite ≥ 0; dias de
fechamento/vencimento válidos (1–31, com ajuste de mês curto em AC-104);
não armazenar número do cartão, CVV, senha ou credenciais bancárias
(AC-051); cartão inativo mantém o histórico e não aceita novas compras
(AC-050).

Editar o dia de fechamento/vencimento não move compras já registradas:
a atribuição à fatura é feita no registro da compra (snapshot).
"""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Category, CreditCard, User
from app.schemas.credit_card import CardCreate, CardUpdate
from app.services.invoices import committed_amount

ZERO = Decimal("0.00")


def list_cards(db: Session, user: User) -> list[dict]:
    cards = list(
        db.scalars(
            select(CreditCard)
            .where(CreditCard.user_id == user.id)
            .order_by(CreditCard.name)
        )
    )
    return [card_payload(db, card) for card in cards]


def get_card(db: Session, user: User, card_id: int) -> dict:
    return card_payload(db, get_owned_card(db, user, card_id))


def create_card(db: Session, user: User, payload: CardCreate) -> dict:
    card = CreditCard(
        user_id=user.id,
        name=payload.name.strip(),
        issuer=payload.issuer.strip() if payload.issuer else None,
        credit_limit=payload.credit_limit,
        closing_day=payload.closing_day,
        due_day=payload.due_day,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card_payload(db, card)


def update_card(db: Session, user: User, card_id: int, payload: CardUpdate) -> dict:
    card = get_owned_card(db, user, card_id)
    if payload.name is not None:
        card.name = payload.name.strip()
    if payload.issuer is not None:
        card.issuer = payload.issuer.strip() or None
    if payload.credit_limit is not None:
        card.credit_limit = payload.credit_limit
    if payload.closing_day is not None:
        card.closing_day = payload.closing_day
    if payload.due_day is not None:
        card.due_day = payload.due_day
    db.commit()
    db.refresh(card)
    return card_payload(db, card)


def set_card_status(db: Session, user: User, card_id: int, is_active: bool) -> dict:
    """Ativa ou inativa o cartão (AC-050). Inativar preserva o histórico."""
    card = get_owned_card(db, user, card_id)
    card.is_active = is_active
    db.commit()
    db.refresh(card)
    return card_payload(db, card)


def get_owned_card(db: Session, user: User, card_id: int) -> CreditCard:
    card = db.scalar(
        select(CreditCard).where(
            CreditCard.id == card_id, CreditCard.user_id == user.id
        )
    )
    if card is None:
        raise AppError(
            code="card_not_found",
            message="Cartão não encontrado.",
            http_status=404,
        )
    return card


def card_payload(db: Session, card: CreditCard) -> dict:
    """Cartão com indicadores de limite (`spec.md` §6.11, T-050)."""
    committed = committed_amount(db, card)
    return {
        "id": card.id,
        "name": card.name,
        "issuer": card.issuer,
        "credit_limit": card.credit_limit,
        "closing_day": card.closing_day,
        "due_day": card.due_day,
        "is_active": card.is_active,
        "committed_amount": committed,
        "available_limit": card.credit_limit - committed,
        "created_at": card.created_at,
    }


def get_owned_category(db: Session, user: User, category_id: int) -> Category:
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
