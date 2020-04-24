"""Rename PollOption to Option

Revision ID: 4a3508ddb972
Revises: 3a87adc2088b
Create Date: 2020-04-21 11:24:08.241925

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4a3508ddb972"
down_revision = "3a87adc2088b"
branch_labels = None
depends_on = None


def upgrade():
    # Rename option table
    op.drop_index("ix_poll_option_poll_id", table_name="poll_option")
    op.rename_table("poll_option", "option")
    op.create_index(op.f("ix_option_poll_id"), "option", ["poll_id"], unique=False)

    # Rename vote.poll_option
    op.drop_constraint("one_vote_per_option_and_user", "vote", type_="unique")
    op.drop_index("ix_vote_poll_option_id", table_name="vote")
    op.drop_constraint("vote_poll_option_id_fkey", "vote", type_="foreignkey")

    op.alter_column("vote", "poll_option_id", new_column_name="option_id")

    op.create_index(op.f("ix_vote_option_id"), "vote", ["option_id"], unique=False)
    op.create_unique_constraint(
        "one_vote_per_option_and_user", "vote", ["user_id", "poll_id", "option_id"]
    )
    op.create_foreign_key(
        "vote_option_id_fkey",
        "vote",
        "option",
        ["option_id"],
        ["id"],
        ondelete="cascade",
    )


def downgrade():
    # Rename option table
    op.drop_index(op.f("ix_option_poll_id"), table_name="option")
    op.rename_table("option", "poll_option")
    op.create_index("ix_poll_option_poll_id", "poll_option", ["poll_id"], unique=False)

    # Rename vote.poll_option
    op.drop_index("ix_vote_option_id", table_name="vote")
    op.drop_constraint("vote_option_id_fkey", "vote", type_="foreignkey")
    op.drop_constraint("one_vote_per_option_and_user", "vote", type_="unique")

    op.alter_column("vote", "option_id", new_column_name="poll_option_id")

    op.create_index(
        op.f("ix_vote_poll_option_id"), "vote", ["poll_option_id"], unique=False
    )
    op.create_foreign_key(
        "vote_poll_option_id_fkey",
        "vote",
        "poll_option",
        ["poll_option_id"],
        ["id"],
        ondelete="cascade",
    )
    op.create_unique_constraint(
        "one_vote_per_option_and_user", "vote", ["user_id", "poll_id", "poll_option_id"]
    )
