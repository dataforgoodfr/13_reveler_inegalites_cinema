"""Create posters table

Revision ID: 70d997a5cc43
Revises: d471dd7a5deb
Create Date: 2025-03-17 19:33:01.898098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70d997a5cc43'
down_revision: Union[str, None] = 'd471dd7a5deb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ric_posters',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('image_base64', sa.String(), nullable=False),
    sa.Column('film_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['film_id'], ['ric_films.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ric_posters')
    # ### end Alembic commands ###
