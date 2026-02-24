"""user_domains and user_domain_tickers with RLS

Revision ID: 05_02_user_domains
Revises: 8325633ad9d9
Create Date: 2026-02-21

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = '05_02_user_domains'
down_revision: Union[str, Sequence[str], None] = '05_01_daily_snapshots'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_domains",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_user_domains_user_id", "user_domains", ["user_id"])
    op.create_table(
        "user_domain_tickers",
        sa.Column("domain_id", sa.Integer(), nullable=False),
        sa.Column("ticker", sa.String(10), nullable=False),
        sa.ForeignKeyConstraint(["domain_id"], ["user_domains.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("domain_id", "ticker"),
    )
    op.execute("ALTER TABLE user_domains ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE user_domain_tickers ENABLE ROW LEVEL SECURITY")
    op.execute(
        """CREATE POLICY own_domains ON user_domains FOR ALL TO authenticated
        USING ((select auth.uid()) = user_id)
        WITH CHECK ((select auth.uid()) = user_id)"""
    )
    op.execute(
        """CREATE POLICY own_tickers ON user_domain_tickers FOR ALL TO authenticated
        USING (domain_id IN (SELECT id FROM user_domains WHERE user_id = (select auth.uid())))"""
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS own_tickers ON user_domain_tickers")
    op.execute("DROP POLICY IF EXISTS own_domains ON user_domains")
    op.drop_table("user_domain_tickers")
    op.drop_index("ix_user_domains_user_id", table_name="user_domains")
    op.drop_table("user_domains")
