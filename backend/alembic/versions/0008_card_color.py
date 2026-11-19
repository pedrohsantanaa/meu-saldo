"""Cor do cartão de crédito (melhoria de interface).

Revision ID: 0008_card_color
Revises: 0007_card_category_budgets
Create Date: 2026-11-19

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008_card_color"
down_revision: str | None = "0007_card_category_budgets"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "credit_cards", sa.Column("color", sa.String(length=20), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("credit_cards", "color")
