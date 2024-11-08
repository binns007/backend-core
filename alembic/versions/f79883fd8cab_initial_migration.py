"""Initial migration

Revision ID: f79883fd8cab
Revises: 
Create Date: 2024-11-08 18:27:25.897652

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f79883fd8cab'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Create base tables first
    op.create_table(
        'dealerships',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(length=100)),
        # other columns here
    )

    # Then create dependent tables
    op.create_table(
        'branches',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('dealership_id', sa.Integer, sa.ForeignKey('dealerships.id', ondelete='CASCADE')),
        # other columns here
    )

def downgrade():
    # Drop dependent tables first
    op.drop_table('branches')
    op.drop_table('dealerships')
