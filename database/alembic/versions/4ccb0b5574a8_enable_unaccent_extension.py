"""enable unaccent extension

Revision ID: 4ccb0b5574a8
Revises: 3010b8ee91ab
Create Date: 2025-04-15 22:51:47.051792

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ccb0b5574a8'
down_revision: Union[str, None] = '3010b8ee91ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Enable unaccent extension (safe if already enabled)
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS unaccent;"))

def downgrade():
    # Optional: remove extensions
    op.execute(sa.text("DROP EXTENSION IF EXISTS unaccent;"))
