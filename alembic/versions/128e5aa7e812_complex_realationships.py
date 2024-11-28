"""complex realationships

Revision ID: 128e5aa7e812
Revises: f4db8834796e
Create Date: 2024-11-27 02:11:51.601063

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '128e5aa7e812'
down_revision: Union[str, None] = 'f4db8834796e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create form_templates table
    op.create_table(
        'form_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_activated_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('dealership_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['dealership_id'], ['dealerships.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_form_templates_id', 'form_templates', ['id'])

    # Create form_fields table
    op.create_table(
        'form_fields',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('field_type', 
                 sa.Enum('text', 'number', 'image', 'date', 'amount', 'vehicle', 
                        name='field_type_enum', create_type=False), 
                 nullable=False),
        sa.Column('filled_by', 
                 sa.Enum('sales_executive', 'customer', 
                        name='filled_by_enum', create_type=False), 
                 nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['template_id'], ['form_templates.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_form_fields_id', 'form_fields', ['id'])

    # Create form_instances table
    op.create_table(
        'form_instances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('generated_by', sa.Integer(), nullable=False),
        sa.Column('customer_name', sa.String(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['form_templates.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_form_instances_id', 'form_instances', ['id'])

    # Create vehicles table
    op.create_table(
        'vehicles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dealership_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('first_service_time', sa.String(), nullable=True),
        sa.Column('service_kms', sa.Integer(), nullable=True),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['dealership_id'], ['dealerships.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_vehicles_id', 'vehicles', ['id'])

    # Create customers table
    op.create_table(
        'customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('form_instance_id', sa.Integer(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('amount_paid', sa.Float(), default=0, nullable=False),
        sa.Column('balance_amount', sa.Float(), default=0, nullable=False),
        sa.Column('dealership_id', sa.Integer(), nullable=True),
        sa.Column('branch_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('vehicle_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['dealership_id'], ['dealerships.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['form_instance_id'], ['form_instances.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_customers_id', 'customers', ['id'])

    # Create form_responses table
    op.create_table(
        'form_responses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('form_instance_id', sa.Integer(), nullable=False),
        sa.Column('form_field_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['form_instance_id'], ['form_instances.id']),
        sa.ForeignKeyConstraint(['form_field_id'], ['form_fields.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create chat_sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('form_instance_id', sa.Integer(), nullable=False),
        sa.Column('customer_name', sa.String(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), default='active'),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('closed_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['form_instance_id'], ['form_instances.id']),
        sa.ForeignKeyConstraint(['employee_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('sender_type', sa.String(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id']),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()')),
        sa.Column('notification_type', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Drop tables in correct order based on dependencies
    op.drop_table('notifications')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('form_responses')
    op.drop_table('customers')
    op.drop_table('vehicles')
    op.drop_table('form_instances')
    op.drop_table('form_fields')
    op.drop_table('form_templates')