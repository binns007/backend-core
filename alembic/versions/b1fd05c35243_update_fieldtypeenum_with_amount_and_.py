"""Update fieldtypeenum with amount and vehicle

Revision ID: b1fd05c35243
Revises: 479b86ef11e7
Create Date: 2024-11-26 14:47:58.350581

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b1fd05c35243'
down_revision: Union[str, None] = '479b86ef11e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define new enum values
new_enum_values = ('text', 'number', 'image', 'date', 'amount', 'vehicle')
old_enum_values = ('text', 'number', 'image', 'date')

def upgrade():
    # Create a temporary enum with the new values
    op.execute("CREATE TYPE fieldtypeenum_new AS ENUM %s;" % str(new_enum_values))

    # Alter the columns using the new enum type
    op.execute(
        """
        ALTER TABLE form_fields ALTER COLUMN field_type
        TYPE fieldtypeenum_new
        USING field_type::TEXT::fieldtypeenum_new;
        """
    )

    # Drop the old enum type and rename the new enum type
    op.execute("DROP TYPE fieldtypeenum;")
    op.execute("ALTER TYPE fieldtypeenum_new RENAME TO fieldtypeenum;")


def downgrade():
    # Create a temporary enum with the old values
    op.execute("CREATE TYPE fieldtypeenum_old AS ENUM %s;" % str(old_enum_values))

    # Alter the columns using the old enum type
    op.execute(
        """
        ALTER TABLE form_fields ALTER COLUMN field_type
        TYPE fieldtypeenum_old
        USING field_type::TEXT::fieldtypeenum_old;
        """
    )

    # Drop the new enum type and rename the old enum type
    op.execute("DROP TYPE fieldtypeenum;")
    op.execute("ALTER TYPE fieldtypeenum_old RENAME TO fieldtypeenum;")