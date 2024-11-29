"""add customer_submitted_at column

Revision ID: 7c4e0ab0a840
Revises: f3b916c14196
Create Date: 2024-11-29 06:51:29.562353

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c4e0ab0a840'
down_revision: Union[str, None] = 'f3b916c14196'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add the new column to the form_instances table
    op.add_column(
        'form_instances',
        sa.Column('customer_submitted_at', sa.TIMESTAMP(timezone=True), nullable=True)
    )


def downgrade():
    # Remove the column in case of a rollback
    op.drop_column('form_instances', 'customer_submitted_at')
    
