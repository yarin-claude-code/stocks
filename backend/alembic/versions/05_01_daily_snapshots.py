"""05_01_daily_snapshots

Revision ID: 05_01_daily_snapshots
Revises: 8325633ad9d9
Create Date: 2026-02-21 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = '05_01_daily_snapshots'
down_revision: Union[str, Sequence[str], None] = 'a1c3e7f2b904'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'daily_snapshots',
        sa.Column('ticker', sa.String(length=10), nullable=False),
        sa.Column('snap_date', sa.Date(), nullable=False),
        sa.Column('composite_score', sa.Float(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('domain_id', sa.Integer(), nullable=True),
        sa.Column('trend_slope', sa.Float(), nullable=False, server_default='0.0'),
        sa.ForeignKeyConstraint(['domain_id'], ['domains.id']),
        sa.PrimaryKeyConstraint('ticker', 'snap_date'),
    )


def downgrade() -> None:
    op.drop_table('daily_snapshots')
