"""basic migrations

Revision ID: f4db8834796e
Revises: 843c1f33c5de
Create Date: 2024-11-27 01:54:20.658558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f4db8834796e'
down_revision: Union[str, None] = '843c1f33c5de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Create branches table
    op.create_table(
        'branches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dealership_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['dealership_id'], ['dealerships.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_branches_id', 'branches', ['id'])

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dealership_id', sa.Integer(), nullable=True),
        sa.Column('branch_id', sa.Integer(), nullable=True),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('role', sa.Enum('admin', 'dealer', 'sales_executive', 'finance', 'rto', 'customer', name='role_enum'), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.Column('is_activated', sa.Boolean(), default=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['dealership_id'], ['dealerships.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_id', 'users', ['id'])

    # Create dealership_roles table
    op.create_table(
        'dealership_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dealership_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('admin', 'dealer', 'sales_executive', 'finance', 'rto', 'customer', name='role_enum'), nullable=False),
        sa.Column('enabled', sa.Boolean(), default=True),
        sa.ForeignKeyConstraint(['dealership_id'], ['dealerships.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_dealership_roles_id', 'dealership_roles', ['id'])

    # Add foreign key to dealerships for creator_id
    op.create_foreign_key(
        'fk_dealerships_creator_id_users',
        'dealerships', 'users',
        ['creator_id'], ['id']
    )

def downgrade():
    op.drop_constraint('fk_dealerships_creator_id_users', 'dealerships', type_='foreignkey')
    op.drop_index('ix_dealership_roles_id', 'dealership_roles')
    op.drop_table('dealership_roles')
    op.drop_index('ix_users_id', 'users')
    op.drop_table('users')
    op.drop_index('ix_branches_id', 'branches')
    op.drop_table('branches')