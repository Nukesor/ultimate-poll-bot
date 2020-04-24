"""Option index

Revision ID: 8a4f079a3260
Revises: 4a3508ddb972
Create Date: 2020-04-21 12:13:49.012503

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import or_
from sqlalchemy.orm.session import Session

# Set system path, so alembic is capable of finding the stickerfinder module
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.getcwd()))
sys.path.append(parent_dir)
from pollbot.models import Poll
from pollbot.db import engine

# revision identifiers, used by Alembic.
revision = "8a4f079a3260"
down_revision = "4a3508ddb972"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("option", sa.Column("index", sa.Integer()))
    op.create_unique_constraint(
        "unique_option_index", "option", ["poll_id", "index"], deferrable=True
    )

    session = Session(bind=op.get_bind())

    count = session.query(Poll).count()
    print(f"Got {count} polls")

    runner = 0
    while runner < count:
        print(runner)
        polls = session.query(Poll).offset(runner).limit(1000).all()

        for poll in polls:
            option_index = 0
            for option in poll.options:
                option.index = option_index
                option_index += 1

        runner += 1000

    # Update sorting enum renames
    session.query(Poll).filter(
        or_(
            Poll.option_sorting == "option_chrono", Poll.option_sorting == "option_name"
        )
    ).update({"option_sorting": "manual"})

    session.query(Poll).filter(Poll.option_sorting == "option_percentage").update(
        {"option_sorting": "percentage"}
    )

    session.query(Poll).filter(Poll.user_sorting == "user_chrono").update(
        {"user_sorting": "chrono"}
    )

    session.query(Poll).filter(Poll.user_sorting == "user_name").update(
        {"user_sorting": "name"}
    )

    session.commit()

    op.alter_column("option", "index", nullable=False)


def downgrade():
    op.drop_constraint("unique_option_index", "option", type_="unique")
    op.drop_column("option", "index")

    session = Session(bind=op.get_bind())
    # Update sorting enum renames
    session.query(Poll).filter(Poll.option_sorting == "manual").update(
        {"option_sorting": "option_chrono"}
    )

    session.query(Poll).filter(Poll.option_sorting == "percentage").update(
        {"option_sorting": "option_percentage"}
    )

    session.query(Poll).filter(Poll.user_sorting == "chrono").update(
        {"user_sorting": "user_chrono"}
    )

    session.query(Poll).filter(Poll.user_sorting == "name").update(
        {"user_sorting": "user_name"}
    )

    session.commit()
