"""add_long_term_score

Revision ID: a1c3e7f2b904
Revises: 8325633ad9d9
Create Date: 2026-02-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1c3e7f2b904'
down_revision = '8325633ad9d9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('ranking_results', sa.Column('long_term_score', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('ranking_results', 'long_term_score')
