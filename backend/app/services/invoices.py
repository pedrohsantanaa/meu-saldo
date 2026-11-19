"""Faturas do cartão de crédito (T-049), limite (T-050) e pagamento (T-051).

Política de contabilização (`spec.md` §7.2): a fatura é a consolidação
das compras do seu ciclo e conta uma única vez, como despesa variável do
mês do seu vencimento. O pagamento é liquidação da obrigação — não gera
despesa de consumo (AC-060) — e libera o limite (AC-106).

O total da fatura nunca é materializado: deriva sempre da soma das
compras atribuídas. `status` é sincronizado a cada mutação:

- ``open``: sem pagamentos;
- ``partial``: pago > 0 e menor que o total;
- ``paid``: pago ≥ total (com total > 0).
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import (
    CreditCard,
    CreditCardInvoice,
    CreditCardInvoicePayment,
    CreditCardPurchase,
    User,
)
from app.schemas.credit_card_invoice import PaymentCreate
from app.services.invoice_cycle import resolve_invoice_cycle

ZERO = Decimal("0.00")


def get_or_create_invoice(
    db: Session, user: User, card: CreditCard, purchase_date: date
) -> CreditCardInvoice:
    """Fatura do ciclo da compra (T-048), criada sob demanda.

    A resolução usa as regras de ciclo aprovadas (AC-101 a AC-105) e o
    resultado é fixado na compra (snapshot).
    """
    cycle = resolve_invoice_cycle(
        card.closing_day, card.due_day, purchase_date, card.created_at.date()
    )
    invoice = db.scalar(
        select(CreditCardInvoice).where(
            CreditCardInvoice.credit_card_id == card.id,
            CreditCardInvoice.reference_month == cycle.reference_month,
        )
    )
    if invoice is None:
        invoice = CreditCardInvoice(
            user_id=user.id,
            credit_card_id=card.id,
            reference_month=cycle.reference_month,
            closing_date=cycle.closing_date,
            due_date=cycle.due_date,
            status="open",
        )
        db.add(invoice)
        db.flush()
    return invoice


def invoice_total(db: Session, invoice: CreditCardInvoice) -> Decimal:
    total = db.scalar(
        select(func.coalesce(func.sum(CreditCardPurchase.total_amount), ZERO)).where(
            CreditCardPurchase.invoice_id == invoice.id
        )
    )
    return Decimal(total)


def paid_total(db: Session, invoice: CreditCardInvoice) -> Decimal:
    total = db.scalar(
        select(func.coalesce(func.sum(CreditCardInvoicePayment.amount), ZERO)).where(
            CreditCardInvoicePayment.invoice_id == invoice.id
        )
    )
    return Decimal(total)


def sync_status(db: Session, invoice: CreditCardInvoice) -> None:
    total = invoice_total(db, invoice)
    paid = paid_total(db, invoice)
    if total > 0 and paid >= total:
        invoice.status = "paid"
    elif paid > 0:
        invoice.status = "partial"
    else:
        invoice.status = "open"


def invoice_payload(db: Session, invoice: CreditCardInvoice) -> dict:
    total = invoice_total(db, invoice)
    paid = paid_total(db, invoice)
    return {
        "id": invoice.id,
        "credit_card_id": invoice.credit_card_id,
        "reference_month": invoice.reference_month,
        "closing_date": invoice.closing_date,
        "due_date": invoice.due_date,
        "status": invoice.status,
        "total": total,
        "paid_amount": paid,
        "open_amount": total - paid,
    }


def list_invoices(db: Session, user: User, card_id: int) -> list[dict]:
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
    invoices = list(
        db.scalars(
            select(CreditCardInvoice)
            .where(
                CreditCardInvoice.user_id == user.id,
                CreditCardInvoice.credit_card_id == card_id,
            )
            .order_by(CreditCardInvoice.due_date.desc())
        )
    )
    return [invoice_payload(db, invoice) for invoice in invoices]


def overview(db: Session, user: User, card: CreditCard) -> dict:
    """Fatura atual e próxima fatura (AC-052).

    Atual = fatura em aberto com vencimento mais próximo (inclui
    vencidas); se todas pagas, a de vencimento mais próximo a partir de
    hoje; na falta de ambas, a última fatura. Próxima = a seguinte por
    vencimento, quando existir.
    """
    invoices = list(
        db.scalars(
            select(CreditCardInvoice)
            .where(
                CreditCardInvoice.user_id == user.id,
                CreditCardInvoice.credit_card_id == card.id,
            )
            .order_by(CreditCardInvoice.due_date)
        )
    )
    if not invoices:
        return {"current": None, "next": None}

    today = date.today()
    current = None
    for invoice in invoices:
        if invoice.status != "paid":
            current = invoice
            break
    if current is None:
        for invoice in invoices:
            if invoice.due_date >= today:
                current = invoice
                break
    if current is None:
        current = invoices[-1]

    following = [inv for inv in invoices if inv.due_date > current.due_date]
    next_invoice = following[0] if following else None
    return {
        "current": invoice_payload(db, current),
        "next": invoice_payload(db, next_invoice) if next_invoice else None,
    }


def get_owned_invoice(
    db: Session, user: User, card_id: int, invoice_id: int
) -> CreditCardInvoice:
    invoice = db.scalar(
        select(CreditCardInvoice).where(
            CreditCardInvoice.id == invoice_id,
            CreditCardInvoice.credit_card_id == card_id,
            CreditCardInvoice.user_id == user.id,
        )
    )
    if invoice is None:
        raise AppError(
            code="invoice_not_found",
            message="Fatura não encontrada.",
            http_status=404,
        )
    return invoice


def invoice_detail_payload(
    db: Session, user: User, card_id: int, invoice_id: int
) -> dict:
    """Fatura com as compras do ciclo e os pagamentos registrados."""
    invoice = get_owned_invoice(db, user, card_id, invoice_id)
    payload = invoice_payload(db, invoice)
    payload["purchases"] = list(
        db.scalars(
            select(CreditCardPurchase)
            .where(CreditCardPurchase.invoice_id == invoice.id)
            .order_by(CreditCardPurchase.purchase_date, CreditCardPurchase.id)
        )
    )
    payload["payments"] = list(
        db.scalars(
            select(CreditCardInvoicePayment)
            .where(CreditCardInvoicePayment.invoice_id == invoice.id)
            .order_by(CreditCardInvoicePayment.paid_at, CreditCardInvoicePayment.id)
        )
    )
    return payload


def register_payment(
    db: Session, user: User, card_id: int, invoice_id: int, payload: PaymentCreate
) -> CreditCardInvoicePayment:
    """Registra pagamento total ou parcial da fatura (T-051).

    Liquidação da obrigação: não cria movimentação nem despesa de
    consumo (AC-060) e libera o limite proporcionalmente (AC-106).
    """
    invoice = get_owned_invoice(db, user, card_id, invoice_id)
    open_amount = invoice_total(db, invoice) - paid_total(db, invoice)
    if open_amount <= ZERO:
        raise AppError(
            code="invoice_already_paid",
            message="Esta fatura já está liquidada.",
            http_status=400,
        )
    if payload.amount > open_amount:
        raise AppError(
            code="payment_exceeds_open_balance",
            message="O pagamento não pode exceder o valor em aberto da fatura.",
            http_status=400,
        )

    payment = CreditCardInvoicePayment(
        user_id=user.id,
        invoice_id=invoice.id,
        amount=payload.amount,
        paid_at=payload.paid_at or date.today(),
    )
    db.add(payment)
    db.flush()
    sync_status(db, invoice)
    db.commit()
    db.refresh(payment)
    return payment


def committed_amount(db: Session, card: CreditCard) -> Decimal:
    """Valor comprometido do cartão (`spec.md` §6.11, T-050).

    Soma das compras atribuídas a faturas ainda não pagas, deduzidos os
    pagamentos já registrados. Pagamento total libera toda a fatura;
    pagamento parcial libera o valor pago (AC-106).
    """
    invoices = list(
        db.scalars(
            select(CreditCardInvoice).where(CreditCardInvoice.credit_card_id == card.id)
        )
    )
    committed = ZERO
    for invoice in invoices:
        remaining = invoice_total(db, invoice) - paid_total(db, invoice)
        if remaining > ZERO:
            committed += remaining
    return committed


def prune_invoice_if_empty(db: Session, invoice: CreditCardInvoice) -> None:
    """Remove fatura sem compras e sem pagamentos (limpeza após edição).

    Faturas com qualquer histórico (compras ou pagamentos) são sempre
    preservadas.
    """
    has_purchases = db.scalar(
        select(CreditCardPurchase.id)
        .where(CreditCardPurchase.invoice_id == invoice.id)
        .limit(1)
    )
    has_payments = db.scalar(
        select(CreditCardInvoicePayment.id)
        .where(CreditCardInvoicePayment.invoice_id == invoice.id)
        .limit(1)
    )
    if has_purchases is None and has_payments is None:
        db.delete(invoice)
