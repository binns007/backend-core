"""Add dealership_id to form_templates

Revision ID: 6f123adba6ea
Revises: 84872e0a99d8
Create Date: 2024-11-20 14:03:52.865539

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f123adba6ea'
down_revision: Union[str, None] = '84872e0a99d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # Step 1: Add `dealership_id` column as nullable
    op.add_column(
        'form_templates',
        sa.Column('dealership_id', sa.Integer(), nullable=True)
    )
    
    # Step 2: Update existing rows with a default dealership_id or NULL
    # (Replace `1` with an appropriate default dealership_id if needed)
    op.execute('UPDATE form_templates SET dealership_id = 1')

    # Step 3: Alter the column to be NOT NULL
    op.alter_column(
        'form_templates',
        'dealership_id',
        nullable=False
    )
    
    # Step 4: Add the foreign key constraint
    op.create_foreign_key(
        'fk_form_templates_dealership_id',
        'form_templates',
        'dealerships',
        ['dealership_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    # Drop the foreign key first
    op.drop_constraint('fk_form_templates_dealership_id', 'form_templates', type_='foreignkey')
    
    # Drop the `dealership_id` column
    op.drop_column('form_templates', 'dealership_id')
