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


class CategoryBudget(Base):
    """Orçamento mensal por categoria, sem cartão (despesas fixas e
    variáveis pagas fora do cartão).

    A combinação usuário + categoria + mês é única (`spec.md` §6.13).
    Os gastos do mês somam as movimentações comuns (tipo despesa) da
    categoria lançadas no mês (`spec.md` §7.2); compras no cartão seguem
    o ciclo da fatura nos orçamentos por cartão e nunca contam aqui.
    O `reference_month` guarda o primeiro dia do mês.
    """

    __tablename__ = "category_budgets"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "category_id",
            "reference_month",
            name="uq_category_budgets_user_category_month",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
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
