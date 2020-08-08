"""Remove user deleted column

Revision ID: 93459304b721
Revises: 128e5c442b84
Create Date: 2020-08-08 11:57:13.009096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "93459304b721"
down_revision = "128e5c442b84"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("user", "deleted")


def downgrade():
    op.add_column(
        "user", sa.Column("deleted", sa.BOOLEAN(), autoincrement=False, nullable=False)
    )
