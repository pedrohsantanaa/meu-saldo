from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.credit_card_invoice import CreditCardInvoice


class CreditCardPurchase(Base):
    """Compra no cartão de crédito (T-046).

    A compra é atribuída a uma fatura no momento do registro (snapshot):
    editar o dia de fechamento do cartão não move compras já registradas
    (preservação de histórico, `design.md` §9.3). Sem parcelamento no MVP
    (T-005): `installments_count` é sempre 1.
    """

    __tablename__ = "credit_card_purchases"
    __table_args__ = (
        Index(
            "ix_card_purchases_user_card_date",
            "user_id",
            "credit_card_id",
            "purchase_date",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    credit_card_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("credit_cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    invoice_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("credit_card_invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    purchase_date: Mapped[date] = mapped_column(nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    installments_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    invoice: Mapped["CreditCardInvoice"] = relationship(lazy="joined")

    @property
    def invoice_reference_month(self) -> date | None:
        """Mês de referência (vencimento) da fatura da compra.

        Exibido pela interface para confirmar em que fatura a compra
        entra (T-076); carregado junto da consulta (lazy="joined").
        """
        if self.invoice is None:
            return None
        return self.invoice.reference_month
