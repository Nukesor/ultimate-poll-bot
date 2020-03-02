"""The sqlalchemy model for a polloption."""
from sqlalchemy import (
    Column,
    func,
    ForeignKey,
)
from sqlalchemy.types import (
    BigInteger,
    Integer,
    DateTime,
    String,
)
from sqlalchemy.orm import relationship

from pollbot.db import base
from pollbot.helper.enums import ReferenceType


class Reference(base):
    """The model for a Reference."""

    __tablename__ = 'reference'

    id = Column(Integer, primary_key=True)
    type = Column(String)
    message_id = Column(BigInteger)
    message_dc_id = Column(BigInteger)
    message_access_hash = Column(BigInteger)
    legacy_inline_message_id = Column(String)

    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='cascade', name='user_fk'), nullable=True, index=True)
    user = relationship('User', foreign_keys='Reference.user_id')

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # ManyToOne
    poll_id = Column(Integer, ForeignKey('poll.id', ondelete='cascade', name="reference_poll"), nullable=False, index=True)
    poll = relationship('Poll')

    def __init__(
        self,
        poll,
        reference_type,
        user=None,
        message_id=None,
        message_dc_id=None,
        message_access_hash=None,
    ):
        """Create a new poll."""
        self.poll = poll
        self.type = reference_type
        self.user = user
        self.message_id = message_id
        self.message_dc_id = message_dc_id
        self.message_access_hash = message_access_hash

    def __repr__(self):
        """Print as string."""
        if self.type == ReferenceType.inline.name:
            message = f'Reference {self.id}: message_id {self.message_id}'
        elif self.type == ReferenceType.admin.name:
            message = f'Reference {self.id}: message_id {self.message_id}, admin: {self.user.id}'
        else:
            message = f'Reference {self.id}: message_id {self.message_id}, user: {self.user.id}'

        return message
