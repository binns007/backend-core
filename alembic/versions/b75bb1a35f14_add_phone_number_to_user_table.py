"""add phone number to user table

Revision ID: b75bb1a35f14
Revises: 0f734d5226ff
Create Date: 2024-11-09 14:07:58.741957

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b75bb1a35f14'
down_revision: Union[str, None] = '0f734d5226ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add phone_number column to users table
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))

def downgrade() -> None:
    # Remove phone_number column from users table
    op.drop_column('users', 'phone_number')
