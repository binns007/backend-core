"""Fix ambiguous foreign key relationships for dealership and users

Revision ID: 9170d2076d93
Revises: 387a00fdfa82
Create Date: 2024-11-07 03:30:16.213076

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '9170d2076d93'
down_revision: Union[str, None] = '387a00fdfa82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Inspect the table to check if the column already exists
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('dealerships')]

    if 'creator_id' not in columns:
        # Add creator_id column in the Dealership table if it doesn't exist
        op.add_column('dealerships', sa.Column('creator_id', sa.Integer(), nullable=False))

        # Add foreign key constraint for creator_id to the users table
        op.create_foreign_key(
            'fk_dealership_creator',  # Name of the foreign key constraint
            'dealerships',            # The source table
            'users',                  # The target table
            ['creator_id'],           # Source column(s)
            ['id'],                   # Target column(s)
            ondelete='CASCADE'        # Optional: define behavior when user is deleted
        )

    # Add dealership_id column in the User table if it doesn't exist
    columns = [col['name'] for col in inspector.get_columns('users')]
    if 'dealership_id' not in columns:
        op.add_column('users', sa.Column('dealership_id', sa.Integer(), nullable=True))

        # Add foreign key constraint for dealership_id to the dealerships table
        op.create_foreign_key(
            'fk_user_dealership',      # Name of the foreign key constraint
            'users',                   # The source table
            'dealerships',             # The target table
            ['dealership_id'],         # Source column(s)
            ['id'],                    # Target column(s)
            ondelete='CASCADE'         # Optional: define behavior when dealership is deleted
        )


def downgrade():
    # Drop foreign key constraints
    op.drop_constraint('fk_dealership_creator', 'dealerships', type_='foreignkey')
    op.drop_constraint('fk_user_dealership', 'users', type_='foreignkey')

    # Drop the columns
    op.drop_column('dealerships', 'creator_id')
    op.drop_column('users', 'dealership_id')