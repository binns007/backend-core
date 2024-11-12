"""Add form_templates and form_fields tables

Revision ID: 4055675380e0
Revises: b75bb1a35f14
Create Date: 2024-11-12 00:49:23.464004

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM



# revision identifiers, used by Alembic.
revision: str = '4055675380e0'
down_revision: Union[str, None] = 'b75bb1a35f14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Define ENUM types
filled_by_enum = ENUM('sales_executive', 'customer', name='filledbyenum', create_type=False)
field_type_enum = ENUM('text', 'number', 'image', 'date', name='fieldtypeenum', create_type=False)


def upgrade():
    # Create ENUM types
    filled_by_enum.create(op.get_bind(), checkfirst=True)
    field_type_enum.create(op.get_bind(), checkfirst=True)

    # Create form_templates table
    op.create_table(
        'form_templates',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('dealership_id', sa.Integer, sa.ForeignKey('dealerships.id', ondelete='CASCADE'))
    )

    # Create form_fields table
    op.create_table(
        'form_fields',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('template_id', sa.Integer, sa.ForeignKey('form_templates.id', ondelete='CASCADE')),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('field_type', field_type_enum, nullable=False),
        sa.Column('is_required', sa.Boolean, default=True),
        sa.Column('filled_by', filled_by_enum, nullable=False),
        sa.Column('order', sa.Integer, nullable=False)
    )


def downgrade():
    # Drop form_fields and form_templates tables
    op.drop_table('form_fields')
    op.drop_table('form_templates')

    # Drop ENUM types
    filled_by_enum.drop(op.get_bind(), checkfirst=True)
    field_type_enum.drop(op.get_bind(), checkfirst=True)