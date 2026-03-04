"""add min_deposits jsonb to casino

Revision ID: c1a2b3d4e5f6
Revises: b03cfc59671b
Create Date: 2026-03-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision: str = 'c1a2b3d4e5f6'
down_revision: Union[str, None] = 'b03cfc59671b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('casinos', sa.Column('min_deposits', JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('casinos', 'min_deposits')
