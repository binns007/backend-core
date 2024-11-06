"""change coloumn password_hash to password in users table

Revision ID: 40edce1d4978
Revises: 9170d2076d93
Create Date: 2024-11-07 03:38:52.902801

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40edce1d4978'
down_revision: Union[str, None] = '9170d2076d93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename the 'password_hash' column to 'password'
    op.alter_column('users', 'password_hash', new_column_name='password')

def downgrade() -> None:
    # Rename the 'password' column back to 'password_hash'
    op.alter_column('users', 'password', new_column_name='password_hash')
