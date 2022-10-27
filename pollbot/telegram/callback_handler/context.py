from __future__ import annotations

from sentry_sdk import add_breadcrumb
from sqlalchemy.orm.scoping import scoped_session

from pollbot.enums import CallbackResult, CallbackType
from pollbot.models import Poll


class CallbackContext:
    """Contains all important information for handling with callbacks."""

    def __init__(self, session: scoped_session, bot, query, user):
        """Create a new CallbackContext from a query."""
        self.bot = bot
        self.query = query
        self.user = user

        # Extract the callback type, task id
        self.data = self.query.data.split(":")
        self.callback_type = CallbackType(int(self.data[0]))
        self.payload = self.data[1]
        try:
            self.action = int(self.data[2])
        except ValueError:
            self.action = self.data[2]

        self.poll = session.query(Poll).get(self.payload)

        # Try to resolve the callback result, if possible
        self.callback_result = None
        try:
            self.callback_result = CallbackResult(self.action)
        except (ValueError, KeyError):
            pass

        if self.query.message:
            # Get chat entity and telegram chat
            self.tg_chat = self.query.message.chat

    def __repr__(self):
        """Print as string."""
        representation = (
            f"Context: query-{self.data}, poll-({self.poll}), user-({self.user}), "
        )
        representation += f"type-{self.callback_type}, action-{self.action}"

        return representation


def get_context(bot, update, session, user):
    """Create a context object for callback queries."""
    context = CallbackContext(session, bot, update.callback_query, user)

    add_breadcrumb(
        crumb={
            "query": update.callback_query,
            "data": update.callback_query.data,
            "user": user,
            "callback_type": context.callback_type,
            "callback_result": context.callback_result,
            "poll": context.poll,
        },
        category="callbacks",
    )

    return context
