"""remove vechicle table

Revision ID: fea89a02c942
Revises: 6a4074588d01
Create Date: 2024-11-24 17:34:34.565231

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fea89a02c942'
down_revision: Union[str, None] = '6a4074588d01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # Drop the foreign key constraint first
    op.drop_constraint('customers_vehicle_id_fkey', 'customers', type_='foreignkey')
    
    # Now drop the "vehicles" table
    op.drop_table('vehicles')


def downgrade():
    # Recreate the "vehicles" table (as before)
    op.create_table(
        'vehicles',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('first_service_time', sa.Integer, nullable=True),
        sa.Column('service_kms', sa.Integer, nullable=True),
        sa.Column('ex_showroom_price', sa.Float, nullable=False),
        # Add additional fields that existed in the "vehicles" table before it was dropped
    )
    
    # Recreate the foreign key constraint
    op.create_foreign_key('customers_vehicle_id_fkey', 'customers', 'vehicles', ['vehicle_id'], ['id'])