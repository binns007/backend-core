"""Add last_activated_at to FormTemplate

Revision ID: b347d1364bbf
Revises: 6f123adba6ea
Create Date: 2024-11-22 11:05:22.925412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b347d1364bbf'
down_revision: Union[str, None] = '815d389bf51a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # Add the last_activated_at column to the users table
    op.add_column(
        'form_templates',
        sa.Column('last_activated_at', sa.TIMESTAMP(timezone=True), nullable=True)
    )


def downgrade():
    # Remove the last_activated_at column from the users table
    op.drop_column('form_templates', 'last_activated_at')