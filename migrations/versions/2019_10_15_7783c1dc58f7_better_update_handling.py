"""Better update handling

Revision ID: 7783c1dc58f7
Revises: 9518199afc55
Create Date: 2019-10-15 20:53:42.038406

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7783c1dc58f7"
down_revision = "9518199afc55"
branch_labels = None
depends_on = None


def upgrade():
    op.execute('DELETE FROM "update";')

    op.add_column("update", sa.Column("next_update", sa.DateTime(), nullable=False))
    op.create_unique_constraint("one_update_per_poll", "update", ["poll_id"])
    op.drop_constraint("one_update_per_time_window", "update", type_="unique")
    op.drop_column("update", "count")
    op.drop_column("update", "updated")
    op.drop_column("update", "time_window")


def downgrade():
    op.add_column(
        "update",
        sa.Column(
            "time_window", postgresql.TIMESTAMP(), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        "update",
        sa.Column("updated", sa.BOOLEAN(), autoincrement=False, nullable=False),
    )
    op.add_column(
        "update", sa.Column("count", sa.INTEGER(), autoincrement=False, nullable=False)
    )
    op.create_unique_constraint(
        "one_update_per_time_window", "update", ["poll_id", "time_window"]
    )
    op.drop_constraint("one_update_per_poll", "update", type_="unique")
    op.drop_column("update", "next_update")
