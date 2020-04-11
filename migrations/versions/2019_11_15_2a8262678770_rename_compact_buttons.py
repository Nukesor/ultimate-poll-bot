"""Rename compact_doodle_buttons to compact_buttons

Revision ID: 2a8262678770
Revises: 15a162b93ce9
Create Date: 2019-11-15 13:14:47.559984

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2a8262678770"
down_revision = "15a162b93ce9"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("poll", "compact_doodle_buttons", new_column_name="compact_buttons")


def downgrade():
    op.alter_column("poll", "compact_buttons", new_column_name="compact_doodle_buttons")
