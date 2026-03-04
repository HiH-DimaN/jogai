"""add_slots_table

Revision ID: d1e2f3a4b5c6
Revises: c1a2b3d4e5f6
Create Date: 2026-03-04

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, None] = "c1a2b3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "slots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("provider", sa.String(length=255), nullable=True),
        sa.Column("rtp", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("volatility", sa.String(length=20), nullable=True),
        sa.Column("max_win", sa.String(length=50), nullable=True),
        sa.Column("reels", sa.Integer(), nullable=True),
        sa.Column("lines", sa.Integer(), nullable=True),
        sa.Column("features", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("tip_pt", sa.Text(), nullable=True),
        sa.Column("tip_es", sa.Text(), nullable=True),
        sa.Column("best_casino_id", sa.Integer(), sa.ForeignKey("casinos.id"), nullable=True),
        sa.Column("geo", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.Column("last_posted_at", sa.DateTime(), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=True),
        sa.Column("source_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        "idx_slots_active_geo",
        "slots",
        ["is_active", "geo"],
        postgresql_where=sa.text("is_active IS TRUE"),
    )
    op.create_index("idx_slots_rtp", "slots", [sa.text("rtp DESC")])
    op.create_index("idx_slots_last_posted", "slots", ["last_posted_at"])


def downgrade() -> None:
    op.drop_index("idx_slots_last_posted", table_name="slots")
    op.drop_index("idx_slots_rtp", table_name="slots")
    op.drop_index("idx_slots_active_geo", table_name="slots")
    op.drop_table("slots")
