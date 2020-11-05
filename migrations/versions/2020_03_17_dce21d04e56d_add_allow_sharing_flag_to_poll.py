"""Add allow_sharing flag to poll

Revision ID: dce21d04e56d
Revises: 21574a420c32
Create Date: 2020-03-17 12:24:35.739577

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dce21d04e56d"
down_revision = "21574a420c32"
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
        sa.Column(
            "allow_sharing", sa.Boolean(), server_default="FALSE", nullable=False
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    """
    Downgrade database.

    Args:
    """
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("poll", "allow_sharing")
    # ### end Alembic commands ###
