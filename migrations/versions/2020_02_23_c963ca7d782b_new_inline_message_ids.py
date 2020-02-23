"""New inline message ids

Revision ID: c963ca7d782b
Revises: f1c0140a53d4
Create Date: 2020-02-23 21:44:43.154888

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c963ca7d782b'
down_revision = 'f1c0140a53d4'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'reference',
        'inline_message_id',
        new_column_name='legacy_inline_message_id',
    )
    op.add_column('reference', sa.Column('inline_message_id', sa.BigInteger(), nullable=True))
    op.add_column('reference', sa.Column('inline_message_dc_id', sa.BigInteger(), nullable=True))
    op.add_column('reference', sa.Column('inline_message_access_hash', sa.BigInteger(), nullable=True))


def downgrade():
    op.drop_column('reference', 'inline_message_id')
    op.drop_column('reference', 'inline_message_dc_id')
    op.drop_column('reference', 'inline_message_access_hash')
    op.alter_column(
        'reference',
        'legacy_inline_message_id',
        new_column_name='inline_message_id',
    )
