"""Remove votes.user_id not null constraint

Revision ID: b167b3275d8e
Revises: 109770ba0d9b
Create Date: 2020-05-05 18:18:14.499418

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b167b3275d8e"
down_revision = "109770ba0d9b"
branch_labels = None
depends_on = None


def upgrade():
    """
    Upgrade database.

    Args:
    """
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("vote", "user_id", existing_type=sa.BIGINT(), nullable=True)
    # ### end Alembic commands ###


def downgrade():
    """
    Downgrade database.

    Args:
    """
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("vote", "user_id", existing_type=sa.BIGINT(), nullable=False)
    # ### end Alembic commands ###
