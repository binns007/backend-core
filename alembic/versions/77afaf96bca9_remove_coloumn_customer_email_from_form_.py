"""remove coloumn customer_email from form_instances

Revision ID: 77afaf96bca9
Revises: b347d1364bbf
Create Date: 2024-11-23 14:42:42.299927

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '77afaf96bca9'
down_revision: Union[str, None] = 'b347d1364bbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Remove the customer_email column from form_instances
    op.drop_column("form_instances", "customer_email")


def downgrade():
    # Add the customer_email column back to form_instances in downgrade
    op.add_column(
        "form_instances",
        sa.Column("customer_email", sa.String, nullable=True)
    )