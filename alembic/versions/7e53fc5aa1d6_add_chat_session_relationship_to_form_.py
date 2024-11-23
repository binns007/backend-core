"""add_chat_session_relationship_to_form_instance

Revision ID: 7e53fc5aa1d6
Revises: d6a8d9a2bccb
Create Date: 2024-11-23 22:56:10.655566

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e53fc5aa1d6'
down_revision: Union[str, None] = 'd6a8d9a2bccb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Ensure all necessary foreign key relationships exist
    op.create_foreign_key(
        'fk_chat_sessions_form_instance',  # Constraint name
        'chat_sessions',                   # Source table
        'form_instances',                  # Target table
        ['form_instance_id'],             # Source columns
        ['id'],                           # Target columns
        ondelete='CASCADE'                # Delete chat sessions when form instance is deleted
    )

def downgrade():
    # Remove the foreign key constraint if needed
    op.drop_constraint(
        'fk_chat_sessions_form_instance', 
        'chat_sessions',
        type_='foreignkey'
    )
