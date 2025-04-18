"""Adjust several film attributes

Revision ID: bf1b7d423a36
Revises: 230802dd9cec
Create Date: 2025-04-02 15:59:19.725118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf1b7d423a36'
down_revision: Union[str, None] = '230802dd9cec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ric_films', sa.Column('visa_number', sa.String(), nullable=True))
    op.add_column('ric_films', sa.Column('allocine_id', sa.Integer(), nullable=True))
    op.drop_column('ric_films', 'bechdel_compliant')
    op.drop_column('ric_films', 'tmdb_id')

    op.drop_column('ric_films', 'cnc_agrement_year')
    op.add_column('ric_films', sa.Column("cnc_agrement_year", sa.Integer(), nullable=True))

    op.drop_column('ric_films', 'asr')
    op.add_column('ric_films', sa.Column('asr', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('ric_films', sa.Column('tmdb_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('ric_films', sa.Column('bechdel_compliant', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('ric_films', 'allocine_id')
    op.drop_column('ric_films', 'visa_number')

    op.drop_column('ric_films', 'cnc_agrement_year')
    op.add_column('ric_films', sa.Column("cnc_agrement_year", sa.DATE(), nullable=True))

    op.drop_column('ric_films', 'asr')
    op.add_column('ric_films', sa.Column("asr", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###
