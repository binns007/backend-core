"""add accounts verified to form instance

Revision ID: ff01959ffd9f
Revises: 7c4e0ab0a840
Create Date: 2024-12-10 18:49:18.246223

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff01959ffd9f'
down_revision: Union[str, None] = '7c4e0ab0a840'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    
    op.add_column('form_instances', 
        sa.Column('accounts_verified', 
            sa.Boolean(), 
            nullable=True, 
            server_default=sa.text('false')
        )
    )
    


def downgrade() -> None:
    

    op.drop_column('form_instances', 'accounts_verified')
    # ### end Alembic commands ###
