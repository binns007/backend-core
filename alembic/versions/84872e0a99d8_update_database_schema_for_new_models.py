"""Update database schema for new models

Revision ID: 84872e0a99d8
Revises: dd81f4147b18
Create Date: 2024-11-20 12:16:57.182053

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84872e0a99d8'
down_revision: Union[str, None] = 'dd81f4147b18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('form_fields', 'template_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_index(op.f('ix_form_fields_id'), 'form_fields', ['id'], unique=False)
    op.drop_constraint('form_fields_template_id_fkey', 'form_fields', type_='foreignkey')
    op.create_foreign_key(None, 'form_fields', 'form_templates', ['template_id'], ['id'])
    op.add_column('form_templates', sa.Column('description', sa.String(), nullable=True))
    op.add_column('form_templates', sa.Column('is_active', sa.Boolean()))
    op.add_column('form_templates', sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.create_index(op.f('ix_form_templates_id'), 'form_templates', ['id'], unique=False)
    op.drop_constraint('form_templates_dealership_id_fkey', 'form_templates', type_='foreignkey')
    op.drop_column('form_templates', 'dealership_id')
    op.alter_column('users', 'is_activated',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('false'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'is_activated',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('false'))
    op.add_column('form_templates', sa.Column('dealership_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('form_templates_dealership_id_fkey', 'form_templates', 'dealerships', ['dealership_id'], ['id'], ondelete='CASCADE')
    op.drop_index(op.f('ix_form_templates_id'), table_name='form_templates')
    op.drop_column('form_templates', 'created_at')
    op.drop_column('form_templates', 'is_active')
    op.drop_column('form_templates', 'description')
    op.drop_constraint(None, 'form_fields', type_='foreignkey')
    op.create_foreign_key('form_fields_template_id_fkey', 'form_fields', 'form_templates', ['template_id'], ['id'], ondelete='CASCADE')
    op.drop_index(op.f('ix_form_fields_id'), table_name='form_fields')
    op.alter_column('form_fields', 'template_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
