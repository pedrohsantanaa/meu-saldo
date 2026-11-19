from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CreditCardInvoicePayment(Base):
    """Pagamento (liquidação) de fatura do cartão (T-051).

    O pagamento liquidia uma obrigação já registrada e **não** gera nova
    despesa de consumo (`spec.md` §7.2, AC-060). Pagamento total ou
    parcial libera o limite do cartão (AC-106).
    """

    __tablename__ = "credit_card_invoice_payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    invoice_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("credit_card_invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    paid_at: Mapped[date] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
