"""The sqlite model for a chat."""
import logging
from sqlalchemy import (
    Column,
    func,
)
from sqlalchemy.types import (
    BigInteger,
    DateTime,
    String,
)
from telegram.error import BadRequest
from sqlalchemy.exc import IntegrityError

from pollbot.db import base
from pollbot.helper.telegram import call_tg_func


class Chat(base):
    """The model for a chat."""

    __tablename__ = 'chat'

    id = Column(BigInteger, primary_key=True)
    type = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __init__(self, chat_id, chat_type):
        """Create a new chat."""
        self.id = chat_id
        self.type = chat_type

    @staticmethod
    def get_or_create(session, chat_id, chat_type):
        """Get or create a new chat."""
        chat = session.query(Chat).get(chat_id)
        if not chat:
            chat = Chat(chat_id, chat_type)
            session.add(chat)
            try:
                session.commit()
            # Handle parallel chat creation
            except IntegrityError as e:
                session.rollback()
                chat = session.query(Chat).get(chat_id)
                if chat is None:
                    raise e

        return chat
