"""Add summarize flag

Revision ID: 17077a9ff72a
Revises: bd06a9545bc4
Create Date: 2019-08-16 18:52:20.926007

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "17077a9ff72a"
down_revision = "bd06a9545bc4"
branch_labels = None
depends_on = None


def upgrade():
    """
    Upgrade database.

    Args:
    """
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "poll",
        sa.Column("summarize", sa.Boolean(), server_default="false", nullable=False),
    )
    # ### end Alembic commands ###


def downgrade():
    """
    Downgrade database.

    Args:
    """
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("poll", "summarize")
    # ### end Alembic commands ###
