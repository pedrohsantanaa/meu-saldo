"""Listagem unificada de movimentações (transações + compras no cartão).

Reúne as movimentações comuns (`Transaction`) e as compras no cartão de
crédito (`CreditCardPurchase`) em uma única lista ordenada pela data do
lançamento, sem nunca transformar uma compra em movimentação comum
(`spec.md` §7.2). Tudo é escopado pelo usuário autenticado.

Regras dos filtros (particularidades respeitadas):

- `type=expense` inclui despesas comuns e compras; `type=card_purchase`
  filtra apenas compras; `income`/`investment` excluem compras;
- `payment_method` comum (dinheiro/pix/debito/outra) vale só para
  movimentações; `credito` filtra apenas compras;
- `card_id` filtra as compras de um cartão (movimentações comuns, sem
  cartão, ficam de fora);
- data, categoria e busca (descrição) valem para os dois tipos — a data
  da compra é `purchase_date`.
"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category, CreditCard, CreditCardPurchase, Transaction, User
from app.services.budgets import month_str
from app.services.transactions import list_transactions

TRANSACTION_TYPES = {"income", "expense", "investment"}
COMMON_PAYMENT_METHODS = {"dinheiro", "pix", "debito", "outra"}


def list_movements(
    db: Session,
    user: User,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    movement_type: str | None = None,
    category_id: int | None = None,
    payment_method: str | None = None,
    card_id: int | None = None,
    search: str | None = None,
) -> list[dict]:
    items: list[dict] = []

    wants_transactions = (
        movement_type != "card_purchase"
        and payment_method != "credito"
        and card_id is None
    )
    wants_purchases = (
        movement_type not in ("income", "investment")
        and payment_method not in COMMON_PAYMENT_METHODS
    )

    if wants_transactions:
        transactions = list_transactions(
            db,
            user,
            date_from=date_from,
            date_to=date_to,
            movement_type=(
                movement_type if movement_type in TRANSACTION_TYPES else None
            ),
            category_id=category_id,
            payment_method=(
                payment_method if payment_method in COMMON_PAYMENT_METHODS else None
            ),
            search=search,
        )
        items.extend(_transaction_payload(item) for item in transactions)

    if wants_purchases:
        purchases = _list_purchases(
            db,
            user,
            date_from=date_from,
            date_to=date_to,
            category_id=category_id,
            card_id=card_id,
            search=search,
        )
        card_names = _card_names(db, {item.credit_card_id for item in purchases})
        expense_types = _category_expense_types(
            db, {item.category_id for item in purchases}
        )
        items.extend(
            _purchase_payload(item, card_names, expense_types) for item in purchases
        )

    items.sort(
        key=lambda item: (item["transaction_date"], item["source"], item["id"]),
        reverse=True,
    )
    return items


def _list_purchases(
    db: Session,
    user: User,
    *,
    date_from: date | None,
    date_to: date | None,
    category_id: int | None,
    card_id: int | None,
    search: str | None,
) -> list[CreditCardPurchase]:
    query = select(CreditCardPurchase).where(CreditCardPurchase.user_id == user.id)
    if date_from is not None:
        query = query.where(CreditCardPurchase.purchase_date >= date_from)
    if date_to is not None:
        query = query.where(CreditCardPurchase.purchase_date <= date_to)
    if category_id is not None:
        query = query.where(CreditCardPurchase.category_id == category_id)
    if card_id is not None:
        query = query.where(CreditCardPurchase.credit_card_id == card_id)
    if search:
        query = query.where(CreditCardPurchase.description.ilike(f"%{search}%"))
    return list(db.scalars(query))


def _card_names(db: Session, card_ids: set[int]) -> dict[int, str]:
    if not card_ids:
        return {}
    return dict(
        db.execute(
            select(CreditCard.id, CreditCard.name).where(CreditCard.id.in_(card_ids))
        ).all()
    )


def _category_expense_types(
    db: Session, category_ids: set[int]
) -> dict[int, str | None]:
    if not category_ids:
        return {}
    return dict(
        db.execute(
            select(Category.id, Category.expense_type).where(
                Category.id.in_(category_ids)
            )
        ).all()
    )


def _transaction_payload(transaction: Transaction) -> dict:
    return {
        "id": transaction.id,
        "source": "transaction",
        "transaction_date": transaction.transaction_date,
        "description": transaction.description,
        "amount": transaction.amount,
        "category_id": transaction.category_id,
        "notes": transaction.notes,
        "type": transaction.type,
        "expense_type": transaction.expense_type,
        "payment_method": transaction.payment_method,
    }


def _purchase_payload(
    purchase: CreditCardPurchase,
    card_names: dict[int, str],
    expense_types: dict[int, str],
) -> dict:
    invoice_reference_month = purchase.invoice_reference_month
    return {
        "id": purchase.id,
        "source": "card_purchase",
        "transaction_date": purchase.purchase_date,
        "description": purchase.description,
        "amount": purchase.total_amount,
        "category_id": purchase.category_id,
        "notes": purchase.notes,
        "type": "expense",
        "expense_type": expense_types.get(purchase.category_id),
        "credit_card_id": purchase.credit_card_id,
        "card_name": card_names.get(purchase.credit_card_id, ""),
        "invoice_reference_month": (
            month_str(invoice_reference_month) if invoice_reference_month else None
        ),
    }
