"""Rename ex_showroom_price to total_price

Revision ID: d1a1bfa7544a
Revises: 67c58a176b93
Create Date: 2024-11-24 21:53:51.713753

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd1a1bfa7544a'
down_revision: Union[str, None] = '67c58a176b93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Rename the column ex_showroom_price to total_price
    op.alter_column(
        table_name='vehicles',
        column_name='ex_showroom_price',
        new_column_name='total_price',
        existing_type=sa.Float,
        existing_nullable=False
    )


def downgrade():
    # Revert the column name back to ex_showroom_price
    op.alter_column(
        table_name='vehicles',
        column_name='total_price',
        new_column_name='ex_showroom_price',
        existing_type=sa.Float,
        existing_nullable=False
    )