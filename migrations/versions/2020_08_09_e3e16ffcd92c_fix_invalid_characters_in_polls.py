"""Fix invalid characters in polls

Revision ID: e3e16ffcd92c
Revises: 93459304b721
Create Date: 2020-08-09 17:08:58.868192

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e3e16ffcd92c"
down_revision = "93459304b721"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        (
            "UPDATE poll SET "
            "name = REPLACE(name, '`', ''), "
            "description = REPLACE(description, '`', '') "
            "WHERE name like '%`%' OR description LIKE '%`%'"
        )
    )


def downgrade():
    pass
