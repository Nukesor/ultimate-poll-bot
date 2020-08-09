"""Remove invalid characters from user.name

Revision ID: 2deadfe1fc65
Revises: e3e16ffcd92c
Create Date: 2020-08-09 17:24:25.603465

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2deadfe1fc65"
down_revision = "e3e16ffcd92c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """UPDATE "user" SET name = REPLACE(name, '`', '') WHERE name like '%`%'"""
    )


def downgrade():
    pass
