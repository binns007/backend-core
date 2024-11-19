"""add is_activated column in users

Revision ID: dd81f4147b18
Revises: 4055675380e0
Create Date: 2024-11-19 12:13:04.455457

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd81f4147b18'
down_revision: Union[str, None] = '4055675380e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('users', sa.Column('is_activated', sa.Boolean(), nullable=False, server_default='false'))

def downgrade():
    op.drop_column('users', 'is_activated')
