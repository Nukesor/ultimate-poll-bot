"""Rename vote type

Revision ID: 5f97163991e5
Revises: f80d0dd2ddac
Create Date: 2019-07-06 12:11:50.404716

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5f97163991e5"
down_revision = "f80d0dd2ddac"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("poll", "vote_type", new_column_name="poll_type")


def downgrade():
    op.alter_column("poll", "poll_type", new_column_name="vote_type")
