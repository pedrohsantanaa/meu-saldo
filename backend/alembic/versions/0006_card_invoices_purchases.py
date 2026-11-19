"""Compras, faturas e pagamentos de cartão de crédito (T-046, T-049, T-051).

Revision ID: 0006_card_invoices_purchases
Revises: 0005_credit_cards
Create Date: 2026-11-19

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_card_invoices_purchases"
down_revision: str | None = "0005_credit_cards"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "credit_card_invoices",
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
        sa.Column("reference_month", sa.Date(), nullable=False),
        sa.Column("closing_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint(
            "credit_card_id",
            "reference_month",
            name="uq_invoices_card_reference_month",
        ),
    )
    op.create_index(
        "ix_credit_card_invoices_user_id", "credit_card_invoices", ["user_id"]
    )
    op.create_index(
        "ix_credit_card_invoices_credit_card_id",
        "credit_card_invoices",
        ["credit_card_id"],
    )
    op.create_index(
        "ix_credit_card_invoices_due_date", "credit_card_invoices", ["due_date"]
    )

    op.create_table(
        "credit_card_purchases",
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
        sa.Column(
            "invoice_id",
            sa.Integer(),
            sa.ForeignKey("credit_card_invoices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("description", sa.String(length=200), nullable=False),
        sa.Column("purchase_date", sa.Date(), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "installments_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index(
        "ix_credit_card_purchases_user_id", "credit_card_purchases", ["user_id"]
    )
    op.create_index(
        "ix_credit_card_purchases_credit_card_id",
        "credit_card_purchases",
        ["credit_card_id"],
    )
    op.create_index(
        "ix_credit_card_purchases_category_id", "credit_card_purchases", ["category_id"]
    )
    op.create_index(
        "ix_credit_card_purchases_invoice_id", "credit_card_purchases", ["invoice_id"]
    )
    op.create_index(
        "ix_card_purchases_user_card_date",
        "credit_card_purchases",
        ["user_id", "credit_card_id", "purchase_date"],
    )

    op.create_table(
        "credit_card_invoice_payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "invoice_id",
            sa.Integer(),
            sa.ForeignKey("credit_card_invoices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("paid_at", sa.Date(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index(
        "ix_credit_card_invoice_payments_user_id",
        "credit_card_invoice_payments",
        ["user_id"],
    )
    op.create_index(
        "ix_credit_card_invoice_payments_invoice_id",
        "credit_card_invoice_payments",
        ["invoice_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_credit_card_invoice_payments_invoice_id",
        table_name="credit_card_invoice_payments",
    )
    op.drop_index(
        "ix_credit_card_invoice_payments_user_id",
        table_name="credit_card_invoice_payments",
    )
    op.drop_table("credit_card_invoice_payments")
    op.drop_index(
        "ix_card_purchases_user_card_date", table_name="credit_card_purchases"
    )
    op.drop_index(
        "ix_credit_card_purchases_invoice_id", table_name="credit_card_purchases"
    )
    op.drop_index(
        "ix_credit_card_purchases_category_id", table_name="credit_card_purchases"
    )
    op.drop_index(
        "ix_credit_card_purchases_credit_card_id", table_name="credit_card_purchases"
    )
    op.drop_index(
        "ix_credit_card_purchases_user_id", table_name="credit_card_purchases"
    )
    op.drop_table("credit_card_purchases")
    op.drop_index("ix_credit_card_invoices_due_date", table_name="credit_card_invoices")
    op.drop_index(
        "ix_credit_card_invoices_credit_card_id", table_name="credit_card_invoices"
    )
    op.drop_index("ix_credit_card_invoices_user_id", table_name="credit_card_invoices")
    op.drop_table("credit_card_invoices")
