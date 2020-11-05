"""Rename in_options

Revision ID: 1f4e87f7575c
Revises: 89a2912d10e3
Create Date: 2019-06-10 15:07:06.724336

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1f4e87f7575c"
down_revision = "89a2912d10e3"
branch_labels = None
depends_on = None


def upgrade():
    """
    Upgrade database.

    Args:
    """
    op.alter_column("poll", "in_options", new_column_name="in_settings")


def downgrade():
    """
    Downgrade database.

    Args:
    """
    op.alter_column("poll", "in_settings", new_column_name="in_options")
