from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class BudgetRecurrence(Base):
    """Recorrência de orçamento: gera as linhas mensais (T-075).

    Dois modos (`spec.md` §6.13): "installments" divide `amount` (valor
    total) em `count` parcelas mensais com soma exata — a última parcela
    absorve os centavos (`spec.md` §7.3); "monthly" repete `amount`
    (valor mensal) por `count` meses. O mês inicial é `start_month` e o
    horizonte é sempre fixo (2 a 60 meses, sem repetição indefinida).
    `credit_card_id` nulo identifica recorrência do orçamento geral (sem
    cartão). Cada mês gerado vira uma linha de orçamento comum com
    `recurrence_id`; editar ou excluir uma linha afeta só aquele mês e a
    exclusão da série remove todas as linhas geradas.
    """

    __tablename__ = "budget_recurrences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    credit_card_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("credit_cards.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)
    start_month: Mapped[date] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
