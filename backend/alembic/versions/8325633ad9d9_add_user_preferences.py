"""add_user_preferences

Revision ID: 8325633ad9d9
Revises: f9bb5673b8f7
Create Date: 2026-02-20 02:48:12.866123

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8325633ad9d9'
down_revision: Union[str, Sequence[str], None] = 'f9bb5673b8f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
          id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
          user_id     uuid NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
          domains     text[] NOT NULL DEFAULT '{}',
          updated_at  timestamptz NOT NULL DEFAULT now()
        )
    """)
    op.execute("ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY "Users manage own preferences" ON user_preferences
          USING (auth.uid() = user_id)
          WITH CHECK (auth.uid() = user_id)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS user_preferences")
