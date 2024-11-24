"""create vehicles table

Revision ID: 67c58a176b93
Revises: fea89a02c942
Create Date: 2024-11-24 17:38:59.257386

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '67c58a176b93'
down_revision: Union[str, None] = 'fea89a02c942'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Create the 'vehicles' table
    op.create_table(
        'vehicles',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('dealership_id', sa.Integer, ForeignKey('dealerships.id'), nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('first_service_time', sa.String, nullable=True),
        sa.Column('service_kms', sa.Integer, nullable=True),
        sa.Column('ex_showroom_price', sa.Float, nullable=False),
    )
    
    # Create the foreign key constraint for dealership
    op.create_foreign_key(
        'fk_vehicles_dealership',  # Name of the constraint
        'vehicles',                # Source table
        'dealerships',             # Target table
        ['dealership_id'],         # Column(s) in the source table
        ['id']                     # Column(s) in the target table
    )
    
    # Create the relationship between vehicles and customers if necessary (optional)
    # (assuming the 'customer' table and the foreign key 'vehicle_id' exist)
    op.create_foreign_key(
        'fk_customers_vehicle',  # Name of the constraint
        'customers',             # Source table
        'vehicles',              # Target table
        ['vehicle_id'],          # Column(s) in the source table
        ['id']                   # Column(s) in the target table
    )


def downgrade():
    # Drop the foreign key constraints
    op.drop_constraint('fk_vehicles_dealership', 'vehicles', type_='foreignkey')
    op.drop_constraint('fk_customers_vehicle', 'customers', type_='foreignkey')
    
    # Drop the 'vehicles' table
    op.drop_table('vehicles')
