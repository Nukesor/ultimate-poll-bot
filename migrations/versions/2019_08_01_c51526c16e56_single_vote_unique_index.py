"""Single vote unique index

Revision ID: c51526c16e56
Revises: dbbc49e3ac86
Create Date: 2019-08-01 02:21:00.078989

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c51526c16e56"
down_revision = "dbbc49e3ac86"
branch_labels = None
depends_on = None


def upgrade():
    """
    Upgrade database.

    Args:
    """
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("vote", sa.Column("poll_type", sa.String(), nullable=True))
    op.create_index(
        "ix_unique_single_vote",
        "vote",
        ["user_id", "poll_id"],
        unique=True,
        postgresql_where=sa.text("poll_type = 'single_vote'"),
    )
    # ### end Alembic commands ###


def downgrade():
    """
    Downgrade database.

    Args:
    """
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_unique_single_vote", table_name="vote")
    op.drop_column("vote", "poll_type")
    # ### end Alembic commands ###
