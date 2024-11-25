from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '479b86ef11e7'
down_revision = 'd1a1bfa7544a'
branch_labels = None
depends_on = None


def upgrade():
    # Add the new value to the ENUM type in PostgreSQL
    op.execute("ALTER TYPE fieldtypeenum ADD VALUE 'vehicle'")


def downgrade():
    # Downgrading ENUM changes is tricky and requires recreating the ENUM
    # Create a temporary ENUM without 'vehicle'
    op.execute("CREATE TYPE fieldtypeenum_temp AS ENUM('text', 'number', 'image', 'date', 'amount')")
    
    # Update columns to use the temporary ENUM
    op.execute(
        """
        ALTER TABLE form_fields
        ALTER COLUMN field_type
        TYPE fieldtypeenum_temp
        USING field_type::TEXT::fieldtypeenum_temp
        """
    )
    
    # Drop the old ENUM
    op.execute("DROP TYPE fieldtypeenum")
    
    # Rename the temporary ENUM to the original name
    op.execute("ALTER TYPE fieldtypeenum_temp RENAME TO fieldtypeenum")
