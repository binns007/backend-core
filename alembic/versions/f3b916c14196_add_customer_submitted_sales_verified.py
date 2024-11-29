"""add customer_submitted , sales_verified

Revision ID: f3b916c14196
Revises: 85df0a82364d
Create Date: 2024-11-29 06:35:06.885320

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3b916c14196'
down_revision: Union[str, None] = '85df0a82364d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Commands to upgrade the database
    op.add_column('form_instances', sa.Column('customer_submitted', sa.Boolean(), nullable=True, server_default=sa.text('FALSE')))
    op.add_column('form_instances', sa.Column('sales_verified', sa.Boolean(), nullable=True, server_default=sa.text('FALSE')))


def downgrade():
    # Commands to downgrade the database
    op.drop_column('form_instances', 'customer_submitted')
    op.drop_column('form_instances', 'sales_verified')