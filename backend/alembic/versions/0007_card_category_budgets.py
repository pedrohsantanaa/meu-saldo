"""Orçamento por cartão e categoria (T-053).

Revision ID: 0007_card_category_budgets
Revises: 0006_card_invoices_purchases
Create Date: 2026-11-19

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007_card_category_budgets"
down_revision: str | None = "0006_card_invoices_purchases"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "card_category_budgets",
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
            "credit_card_id",
            "category_id",
            "reference_month",
            name="uq_budgets_user_card_category_month",
        ),
    )
    op.create_index(
        "ix_card_category_budgets_user_id", "card_category_budgets", ["user_id"]
    )
    op.create_index(
        "ix_card_category_budgets_credit_card_id",
        "card_category_budgets",
        ["credit_card_id"],
    )
    op.create_index(
        "ix_card_category_budgets_category_id",
        "card_category_budgets",
        ["category_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_card_category_budgets_category_id", table_name="card_category_budgets"
    )
    op.drop_index(
        "ix_card_category_budgets_credit_card_id", table_name="card_category_budgets"
    )
    op.drop_index(
        "ix_card_category_budgets_user_id", table_name="card_category_budgets"
    )
    op.drop_table("card_category_budgets")
