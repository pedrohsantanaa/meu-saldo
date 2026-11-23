from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CardCategoryBudget(Base):
    """Orçamento mensal por categoria e cartão (T-053).

    A combinação usuário + cartão + categoria + mês é única
    (`spec.md` §6.13). O mês segue o mesmo ciclo da fatura: os gastos do
    mês são as compras atribuídas à fatura com vencimento naquele mês
    (`spec.md` §7.2, T-003). O `reference_month` guarda o primeiro dia
    do mês.
    """

    __tablename__ = "card_category_budgets"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "credit_card_id",
            "category_id",
            "reference_month",
            name="uq_budgets_user_card_category_month",
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
    reference_month: Mapped[date] = mapped_column(nullable=False)
    budget_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    recurrence_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("budget_recurrences.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
