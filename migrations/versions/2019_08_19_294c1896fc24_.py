"""empty message

Revision ID: 294c1896fc24
Revises: 1197d4b7ce86
Create Date: 2019-08-19 15:01:36.531498

"""
from alembic import op

import os
import sys
from sqlalchemy.orm.session import Session

# Set system path, so alembic is capable of finding the stickerfinder module
parent_dir = os.path.abspath(os.path.join(os.getcwd()))
sys.path.append(parent_dir)
from pollbot.models import Poll, User

# revision identifiers, used by Alembic.
revision = "294c1896fc24"
down_revision = "1197d4b7ce86"
branch_labels = None
depends_on = None


def upgrade():
    session = Session(bind=op.get_bind())

    for language in ["english", "german", "polish", "turkish"]:
        session.query(Poll).filter(Poll.locale == language).update(
            {"locale": language.capitalize()}
        )

        session.query(User).filter(User.locale == language).update(
            {"locale": language.capitalize()}
        )


def downgrade():
    pass
