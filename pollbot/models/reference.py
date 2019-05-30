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


class Reference(base):
    """The model for a Reference."""

    __tablename__ = 'reference'

    id = Column(Integer, primary_key=True)
    admin_chat_id = Column(BigInteger)
    admin_message_id = Column(BigInteger)
    inline_message_id = Column(String)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # ManyToOne
    poll_id = Column(Integer, ForeignKey('poll.id', ondelete='cascade', ), nullable=False, index=True)
    poll = relationship('Poll')

    def __init__(
        self, poll,
        inline_message_id=None,
        admin_chat_id=None,
        admin_message_id=None
    ):
        """Create a new poll."""
        self.poll = poll
        self.inline_message_id = inline_message_id
        self.admin_chat_id = admin_chat_id
        self.admin_message_id = admin_message_id
