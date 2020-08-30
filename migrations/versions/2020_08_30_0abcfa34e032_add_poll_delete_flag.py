"""Add poll.delete flag

Revision ID: 0abcfa34e032
Revises: 2deadfe1fc65
Create Date: 2020-08-30 15:51:30.532569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0abcfa34e032"
down_revision = "2deadfe1fc65"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("poll", sa.Column("delete", sa.String(), nullable=True))


def downgrade():
    op.drop_column("poll", "delete")
