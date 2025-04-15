"""Add index on films original_name with pg_trgm extension

Revision ID: a932df5ac027
Revises: bf1b7d423a36
Create Date: 2025-04-12 09:37:46.198970

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a932df5ac027'
down_revision: Union[str, None] = 'bf1b7d423a36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Enable pg_trgm extension
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Create GIN index on lower(original_name) for similarity search
    op.create_index('film_original_name_trgm_idx', 'ric_films', ['original_name'], unique=False, postgresql_using='gin', postgresql_ops={'original_name': 'gin_trgm_ops'})
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the GIN index
    op.drop_index('film_original_name_trgm_idx', table_name='ric_films', postgresql_using='gin', postgresql_ops={'original_name': 'gin_trgm_ops'})
    
    # Optionally remove the extension (only if not used elsewhere)
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
    # ### end Alembic commands ###

