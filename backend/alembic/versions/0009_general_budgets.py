"""Orçamento por categoria sem cartão (despesas fixas e variáveis).

Revision ID: 0009_general_budgets
Revises: 0008_card_color
Create Date: 2026-11-23

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0009_general_budgets"
down_revision: str | None = "0008_card_color"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "category_budgets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("categories.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("reference_month", sa.Date(), nullable=False),
        sa.Column("budget_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint(
            "user_id",
            "category_id",
            "reference_month",
            name="uq_category_budgets_user_category_month",
        ),
    )
    op.create_index("ix_category_budgets_user_id", "category_budgets", ["user_id"])
    op.create_index(
        "ix_category_budgets_category_id", "category_budgets", ["category_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_category_budgets_category_id", table_name="category_budgets")
    op.drop_index("ix_category_budgets_user_id", table_name="category_budgets")
    op.drop_table("category_budgets")
