"""add is_required coloum to form_fields

Revision ID: 4cd98d69c086
Revises: c14ee0db99d4
Create Date: 2024-11-28 19:52:33.180231

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4cd98d69c086'
down_revision: Union[str, None] = 'c14ee0db99d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.add_column('form_fields', sa.Column('is_required', sa.Boolean(), nullable=False, server_default='false'))

def downgrade():
    op.drop_column('form_fields', 'is_required')