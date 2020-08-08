"""Non-nullable votes

Revision ID: 128e5c442b84
Revises: ff4a8e283767
Create Date: 2020-08-08 11:48:40.573104

"""
from alembic import op
import sqlalchemy as sa

import os
import sys
from sqlalchemy.orm.session import Session

# Set system path, so alembic is capable of finding the stickerfinder module
parent_dir = os.path.abspath(os.path.join(os.getcwd()))
sys.path.append(parent_dir)
from pollbot.models import Vote
from pollbot.db import engine

# revision identifiers, used by Alembic.
revision = "128e5c442b84"
down_revision = "ff4a8e283767"
branch_labels = None
depends_on = None


def upgrade():
    session = Session(bind=op.get_bind())
    polls = session.query(Vote).filter(Vote.user_id.is_(None)).delete()

    op.alter_column("vote", "user_id", existing_type=sa.BIGINT(), nullable=False)


def downgrade():
    op.alter_column("vote", "user_id", existing_type=sa.BIGINT(), nullable=True)
