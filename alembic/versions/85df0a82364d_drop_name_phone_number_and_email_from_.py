"""drop name, phone_number, and email from customers

Revision ID: 85df0a82364d
Revises: 4cd98d69c086
Create Date: 2024-11-29 01:15:52.963417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85df0a82364d'
down_revision: Union[str, None] = '4cd98d69c086'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop columns from the `customers` table
    with op.batch_alter_table("customers") as batch_op:
        batch_op.drop_column("name")
        batch_op.drop_column("phone_number")
        batch_op.drop_column("email")


def downgrade():
    # Add columns back to the `customers` table
    with op.batch_alter_table("customers") as batch_op:
        batch_op.add_column(sa.Column("name", sa.String(), nullable=False))
        batch_op.add_column(sa.Column("phone_number", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("email", sa.String(), unique=True, nullable=True))
