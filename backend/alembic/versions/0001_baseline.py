"""Baseline inicial (sem alterações).

As entidades do meuSaldo serão adicionadas em migrações das próximas fases.

Revision ID: 0001_baseline
Revises:
Create Date: 2026-11-18

"""

from collections.abc import Sequence

revision: str = "0001_baseline"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Baseline: nenhuma alteração de schema nesta revisão.
    pass


def downgrade() -> None:
    pass
