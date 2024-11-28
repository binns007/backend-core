"""update_dealership_role_enum

Revision ID: c14ee0db99d4
Revises: 128e5aa7e812
Create Date: 2024-11-28 18:59:03.308962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c14ee0db99d4'
down_revision: Union[str, None] = '128e5aa7e812'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('dealership_roles', 'role',
                    type_=sa.Enum('admin', 'dealer', 'sales_executive', 'finance', 'rto', 'customer', name='role_enum'),
                    existing_nullable=False)

def downgrade():
    op.alter_column('dealership_roles', 'role',
                    type_=sa.String(),
                    existing_nullable=False)