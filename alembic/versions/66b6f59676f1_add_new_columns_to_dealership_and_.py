"""Add new columns to Dealership and create DealershipRole and SuggestedRole tables

Revision ID: 66b6f59676f1
Revises: ae09f9e4d644
Create Date: 2024-11-07 01:01:59.261024

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.sql import text



# revision identifiers, used by Alembic.
revision: str = '66b6f59676f1'
down_revision: Union[str, None] = 'ae09f9e4d644'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the RoleEnum type without creating it upfront
role_enum = ENUM('ADMIN', 'DEALER', 'SALES_EXECUTIVE', 'FINANCE', 'RTO', 'CUSTOMER', name='roleenum', create_type=False)

def upgrade():
    conn = op.get_bind()

    # Only create the enum if it doesn’t already exist
    if not conn.execute(text("SELECT 1 FROM pg_type WHERE typname = 'roleenum'")).scalar():
        role_enum.create(conn)

    # Add columns to the Dealership table
    op.add_column('dealerships', sa.Column('address', sa.String, nullable=False))
    op.add_column('dealerships', sa.Column('contact_number', sa.String, nullable=False))
    op.add_column('dealerships', sa.Column('num_employees', sa.Integer, nullable=False))

    # Create DealershipRole table
    op.create_table(
        'dealership_roles',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('dealership_id', sa.Integer, sa.ForeignKey('dealerships.id'), nullable=False),
        sa.Column('role', role_enum, nullable=False),
        sa.Column('enabled', sa.Boolean, default=True),
    )

    # Create SuggestedRole table
    op.create_table(
        'suggested_roles',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('dealership_id', sa.Integer, sa.ForeignKey('dealerships.id'), nullable=False),
        sa.Column('role_name', sa.String, nullable=False),
        sa.Column('reason', sa.String),
    )

def downgrade():
    # Drop SuggestedRole and DealershipRole tables
    op.drop_table('suggested_roles')
    op.drop_table('dealership_roles')

    # Remove columns from Dealership table
    op.drop_column('dealerships', 'address')
    op.drop_column('dealerships', 'contact_number')
    op.drop_column('dealerships', 'num_employees')

    # Drop RoleEnum type if it exists
    conn = op.get_bind()
    if conn.execute(text("SELECT 1 FROM pg_type WHERE typname = 'roleenum'")).scalar():
        role_enum.drop(conn)