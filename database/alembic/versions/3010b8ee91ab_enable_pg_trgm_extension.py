"""enable pg_trgm extension

Revision ID: 3010b8ee91ab
Revises: bf1b7d423a36
Create Date: 2025-04-15 21:46:47.517503

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3010b8ee91ab'
down_revision: Union[str, None] = 'bf1b7d423a36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Enable pg_trgm extension (safe if already enabled)
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))

def downgrade():
    # Optional: remove extension
    op.execute(sa.text("DROP EXTENSION IF EXISTS pg_trgm;"))
