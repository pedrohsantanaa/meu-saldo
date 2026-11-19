from datetime import date, datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CreditCardInvoice(Base):
    """Fatura do cartão de crédito (T-049).

    Agrupa as compras de um ciclo de cobrança. A fatura é identificada
    pelo mês do seu vencimento (`spec.md` §7.2): "fatura de janeiro" é a
    que vence em janeiro. O `reference_month` guarda o primeiro dia desse
    mês. O total é sempre a soma das compras atribuídas (não é
    materializado); `status` é sincronizado a cada compra/pagamento.
    """

    __tablename__ = "credit_card_invoices"
    __table_args__ = (
        UniqueConstraint(
            "credit_card_id",
            "reference_month",
            name="uq_invoices_card_reference_month",
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
    reference_month: Mapped[date] = mapped_column(nullable=False)
    closing_date: Mapped[date] = mapped_column(nullable=False)
    due_date: Mapped[date] = mapped_column(nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
