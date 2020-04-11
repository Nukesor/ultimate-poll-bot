"""Add option description

Revision ID: 1a668c8e3285
Revises: 5e263928cf38
Create Date: 2019-06-26 19:36:08.324727

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1a668c8e3285"
down_revision = "5e263928cf38"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("poll_option", sa.Column("description", sa.String(), nullable=True))
    op.alter_column("poll_option", "name", existing_type=sa.VARCHAR(), nullable=False)


def downgrade():
    op.alter_column("poll_option", "name", existing_type=sa.VARCHAR(), nullable=True)
    op.drop_column("poll_option", "description")
