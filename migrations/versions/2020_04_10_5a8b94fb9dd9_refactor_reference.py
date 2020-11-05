"""Refactor Reference

Revision ID: 5a8b94fb9dd9
Revises: c963ca7d782b
Create Date: 2020-03-02 01:16:26.228745

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5a8b94fb9dd9"
down_revision = "f1c0140a53d4"
branch_labels = None
depends_on = None


def upgrade():
    """
    Upgrade database.

    Args:
    """
    # ### commands auto generated by Alembic - please adjust! ###

    op.add_column("reference", sa.Column("message_id", sa.BigInteger(), nullable=True))
    op.add_column(
        "reference", sa.Column("message_dc_id", sa.BigInteger(), nullable=True)
    )
    op.add_column(
        "reference", sa.Column("message_access_hash", sa.BigInteger(), nullable=True)
    )

    op.add_column("reference", sa.Column("type", sa.String(), nullable=True))
    op.add_column("reference", sa.Column("user_id", sa.BigInteger(), nullable=True))
    op.create_index(
        op.f("ix_reference_user_id"), "reference", ["user_id"], unique=False
    )
    op.create_foreign_key(
        "user_fk", "reference", "user", ["user_id"], ["id"], ondelete="cascade"
    )

    op.execute(
        "UPDATE reference SET type = 'inline' WHERE inline_message_id is not NULL"
    )

    op.execute(
        "UPDATE reference \
               SET type='admin', message_id=admin_message_id, user_id=admin_user_id \
                  WHERE admin_user_id is not NULL;"
    )

    op.execute(
        "UPDATE reference \
               SET type='private_vote', message_id=vote_message_id, user_id=vote_user_id \
                  WHERE vote_user_id is not NULL;"
    )

    op.drop_index("ix_reference_vote_user_id", table_name="reference")
    op.drop_constraint("vote_user", "reference", type_="foreignkey")
    op.drop_column("reference", "vote_user_id")
    op.drop_column("reference", "vote_message_id")

    op.drop_index("ix_reference_admin_user_id", table_name="reference")
    op.drop_constraint("admin_user", "reference", type_="foreignkey")
    op.drop_column("reference", "admin_user_id")
    op.drop_column("reference", "admin_message_id")

    op.alter_column(
        "reference",
        "inline_message_id",
        new_column_name="bot_inline_message_id",
    )


def downgrade():
    """
    Upgrade database.

    Args:
    """
    op.add_column(
        "reference",
        sa.Column("admin_user_id", sa.BIGINT(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "reference",
        sa.Column("admin_message_id", sa.BIGINT(), autoincrement=False, nullable=True),
    )
    op.create_foreign_key(
        "admin_user", "reference", "user", ["admin_user_id"], ["id"], ondelete="CASCADE"
    )
    op.create_index(
        "ix_reference_admin_user_id", "reference", ["admin_user_id"], unique=False
    )

    op.add_column(
        "reference",
        sa.Column("vote_user_id", sa.BIGINT(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "reference",
        sa.Column("vote_message_id", sa.BIGINT(), autoincrement=False, nullable=True),
    )
    op.create_foreign_key(
        "vote_user", "reference", "user", ["vote_user_id"], ["id"], ondelete="CASCADE"
    )
    op.create_index(
        "ix_reference_vote_user_id", "reference", ["vote_user_id"], unique=False
    )

    op.execute(
        "UPDATE reference \
               SET admin_message_id=message_id, admin_user_id=user_id \
                  WHERE type = 'admin';"
    )

    op.execute(
        "UPDATE reference \
               SET vote_message_id=message_id, vote_user_id=user_id \
                  WHERE type='private_vote';"
    )

    op.drop_constraint("user_fk", "reference", type_="foreignkey")
    op.drop_index(op.f("ix_reference_user_id"), table_name="reference")

    op.alter_column(
        "reference",
        "bot_inline_message_id",
        new_column_name="inline_message_id",
    )

    op.drop_column("reference", "message_id")
    op.drop_column("reference", "message_dc_id")
    op.drop_column("reference", "message_access_hash")

    op.drop_column("reference", "user_id")
    op.drop_column("reference", "type")
