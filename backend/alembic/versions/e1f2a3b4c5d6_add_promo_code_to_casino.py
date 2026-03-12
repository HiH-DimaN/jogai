"""Add promo_code to casino

Revision ID: e1f2a3b4c5d6
Revises: d1e2f3a4b5c6
Create Date: 2026-03-12

"""
from alembic import op
import sqlalchemy as sa

revision = "e1f2a3b4c5d6"
down_revision = "d1e2f3a4b5c6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("casinos", sa.Column("promo_code", sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column("casinos", "promo_code")
