"""customer table and form instance changes

Revision ID: 6a4074588d01
Revises: 7e53fc5aa1d6
Create Date: 2024-11-24 17:21:00.483477

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6a4074588d01'
down_revision: Union[str, None] = '7e53fc5aa1d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add form_instance_id column with ForeignKey to form_instances
    op.add_column(
        'customers',
        sa.Column('form_instance_id', sa.Integer, sa.ForeignKey('form_instances.id', ondelete="CASCADE"), nullable=False)
    )

    # Add new columns for payments
    op.add_column('customers', sa.Column('total_price', sa.Float(), nullable=False))
    op.add_column('customers', sa.Column('amount_paid', sa.Float(), default=0, nullable=False))
    op.add_column('customers', sa.Column('balance_amount', sa.Float(), default=0, nullable=False))


def downgrade():
    # Remove added columns
    op.drop_column('customers', 'balance_amount')
    op.drop_column('customers', 'amount_paid')
    op.drop_column('customers', 'total_price')
    op.drop_column('customers', 'form_instance_id')