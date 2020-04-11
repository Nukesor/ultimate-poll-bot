"""Allow users to add options

Revision ID: 5e263928cf38
Revises: 7fe81a5d2f88
Create Date: 2019-06-17 16:48:47.098570

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

import os
import sys
from sqlalchemy.orm.session import Session

# Set system path, so alembic is capable of finding the stickerfinder module
parent_dir = os.path.abspath(os.path.join(os.getcwd()))
sys.path.append(parent_dir)
from pollbot.models import Poll
from pollbot.db import engine

# revision identifiers, used by Alembic.
revision = "5e263928cf38"
down_revision = "7fe81a5d2f88"
branch_labels = None
depends_on = None


def upgrade():
    with engine.connect() as con:
        con.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.add_column(
        "poll",
        sa.Column(
            "allow_new_options", sa.Boolean(), server_default="false", nullable=False
        ),
    )
    op.add_column(
        "poll",
        sa.Column(
            "uuid",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
    )
    op.create_unique_constraint("unique_poll_uuid", "poll", ["uuid"])
    op.add_column("user", sa.Column("expected_input", sa.String(), nullable=True))
    op.alter_column(
        "user",
        "current_poll_id",
        existing_type=sa.INTEGER(),
        type_=sa.BigInteger(),
        existing_nullable=True,
    )

    session = Session(bind=op.get_bind())
    polls = session.query(Poll).all()

    for poll in polls:
        poll.user.expected_input = poll.expected_input


def downgrade():
    op.alter_column(
        "user",
        "current_poll_id",
        existing_type=sa.BigInteger(),
        type_=sa.INTEGER(),
        existing_nullable=True,
    )
    op.drop_constraint("unique_poll_uuid", "poll", type_="unique")
    op.drop_column("poll", "uuid")
    op.drop_column("poll", "allow_new_options")

    session = Session(bind=op.get_bind())
    polls = session.query(Poll).all()

    for poll in polls:
        poll.expected_input = poll.user.expected_input

    op.drop_column("user", "expected_input")
