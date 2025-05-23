"""Create film_country_budget_allocations table

Revision ID: 2eedb52b923f
Revises: b50425a00467
Create Date: 2025-03-17 19:00:17.605634

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2eedb52b923f'
down_revision: Union[str, None] = 'b50425a00467'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ric_film_country_budget_allocations',
    sa.Column('country_id', sa.Integer(), nullable=False),
    sa.Column('film_id', sa.Integer(), nullable=False),
    sa.Column('budget_allocation', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['country_id'], ['ric_countries.id'], ),
    sa.ForeignKeyConstraint(['film_id'], ['ric_films.id'], ),
    sa.PrimaryKeyConstraint('country_id', 'film_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ric_film_country_budget_allocations')
    # ### end Alembic commands ###
