"""Recorrência de orçamento: parcelas e repetição mensal (T-075).

Revision ID: 0010_budget_recurrences
Revises: 0009_general_budgets
Create Date: 2026-11-23

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0010_budget_recurrences"
down_revision: str | None = "0009_general_budgets"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

BUDGET_TABLES = ("card_category_budgets", "category_budgets")


def upgrade() -> None:
    op.create_table(
        "budget_recurrences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "credit_card_id",
            sa.Integer(),
            sa.ForeignKey("credit_cards.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("categories.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("mode", sa.String(20), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("start_month", sa.Date(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_budget_recurrences_user_id", "budget_recurrences", ["user_id"])
    op.create_index(
        "ix_budget_recurrences_credit_card_id",
        "budget_recurrences",
        ["credit_card_id"],
    )
    op.create_index(
        "ix_budget_recurrences_category_id", "budget_recurrences", ["category_id"]
    )

    for table in BUDGET_TABLES:
        op.add_column(
            table,
            sa.Column(
                "recurrence_id",
                sa.Integer(),
                sa.ForeignKey("budget_recurrences.id", ondelete="CASCADE"),
                nullable=True,
            ),
        )
        op.create_index(
            f"ix_{table}_recurrence_id", table, ["recurrence_id"]
        )


def downgrade() -> None:
    for table in reversed(BUDGET_TABLES):
        op.drop_index(f"ix_{table}_recurrence_id", table_name=table)
        op.drop_column(table, "recurrence_id")

    op.drop_index("ix_budget_recurrences_category_id", table_name="budget_recurrences")
    op.drop_index(
        "ix_budget_recurrences_credit_card_id", table_name="budget_recurrences"
    )
    op.drop_index("ix_budget_recurrences_user_id", table_name="budget_recurrences")
    op.drop_table("budget_recurrences")
