"""initial migration

Revision ID: 843c1f33c5de
Revises: 
Create Date: 2024-11-27 01:52:44.692265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision: str = '843c1f33c5de'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade():
    # Create dealerships table
    op.create_table(
        'dealerships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('contact_email', sa.String(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('contact_number', sa.String(), nullable=False),
        sa.Column('num_employees', sa.Integer(), nullable=False),
        sa.Column('num_branches', sa.Integer(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contact_email')
    )
    op.create_index('ix_dealerships_id', 'dealerships', ['id'])

    # Create OTP table
    op.create_table(
        'otps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('otp_code', sa.String(), nullable=False),
        sa.Column('expiration_time', sa.DateTime(), nullable=False),
        sa.Column('verified', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_otps_id', 'otps', ['id'])
    op.create_index('ix_otps_email', 'otps', ['email'])


def downgrade():
    op.drop_index('ix_otps_email', 'otps')
    op.drop_index('ix_otps_id', 'otps')
    op.drop_table('otps')
    op.drop_index('ix_dealerships_id', 'dealerships')
    op.drop_table('dealerships')