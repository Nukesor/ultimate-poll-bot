"""Callback query handling."""
from datetime import date
from raven import breadcrumbs
from telegram.ext import run_async
from sqlalchemy.exc import IntegrityError

from pollbot.helper.stats import increase_stat, increase_user_stat
from pollbot.helper.session import callback_query_wrapper
from pollbot.helper.enums import CallbackType, CallbackResult
from pollbot.models import Poll, Option, UserStatistic

from .vote import handle_vote
from .mapping import async_callback_mapping, callback_mapping


class CallbackContext:
    """Contains all important information for handling with callbacks."""

    def __init__(self, session, bot, query, user):
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
        except:
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

    breadcrumbs.record(
        data={
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


@callback_query_wrapper
def handle_callback_query(bot, update, session, user):
    """Handle synchronous callback queries.

    Some critical callbacks shouldn't be allowed to be asynchronous,
    since they tend to cause race conditions and integrity errors in the database
    schema. That's why some calls are restricted to be synchronous.
    """
    context = get_context(bot, update, session, user)
    print("Synchronous")

    increase_user_stat(session, context.user, "callback_calls")
    session.commit()
    response = callback_mapping[context.callback_type](session, context)

    # Callback handler functions always return the callback answer
    # The only exception is the vote function, which is way too complicated and
    # implements its own callback query answer logic.
    if response is not None and context.callback_type != CallbackType.vote:
        context.query.answer(response)
    else:
        context.query.answer("")

    increase_stat(session, "callback_calls")

    return


@run_async
@callback_query_wrapper
def handle_async_callback_query(bot, update, session, user):
    """Handle asynchronous callback queries.

    Most callback queries are unproblematic in terms of causing race-conditions.
    Thereby they can be handled asynchronously.

    However, we do handle votes asynchronously as an edge-case, since we want those
    calls to be handled as fast as possible.

    The race condition handling for votes is handled in the respective `handle_vote` function.
    """
    context = get_context(bot, update, session, user)
    print("Asynchronous")

    # Vote logic needs some special handling
    if context.callback_type == CallbackType.vote:
        option = session.query(Option).get(context.payload)
        if option is None:
            return

        poll = option.poll

        # Ensure user statistics exist for this poll owner
        # We need to track at least some user activity, since there seem to be some users which
        # abuse the bot by creating polls and spamming up to 1 million votes per day.
        #
        # I really hate doing this, but I don't see another way to prevent DOS attacks
        # without tracking at least some numbers.
        user_statistic = session.query(UserStatistic).get((date.today(), poll.user.id))

        if user_statistic is None:
            user_statistic = UserStatistic(poll.user)
            session.add(user_statistic)
            try:
                session.commit()
            # Handle race condition for parallel user statistic creation
            # Return the statistic that has already been created in another session
            except IntegrityError as e:
                session.rollback()
                user_statistic = session.query(UserStatistic).get(
                    (date.today(), poll.user.id)
                )
                if user_statistic is None:
                    raise e

        # Increase stats before we do the voting logic
        # Otherwise the user might dos the bot by triggering flood exceptions
        # before actually being able to increase the stats
        increase_user_stat(session, context.user, "votes")
        increase_user_stat(session, poll.user, "poll_callback_calls")

        session.commit()
        response = handle_vote(session, context, option)

    else:
        increase_user_stat(session, context.user, "callback_calls")
        session.commit()
        response = async_callback_mapping[context.callback_type](session, context)

    # Callback handler functions always return the callback answer
    # The only exception is the vote function, which is way too complicated and
    # implements its own callback query answer logic.
    if response is not None and context.callback_type != CallbackType.vote:
        context.query.answer(response)
    else:
        context.query.answer("")

    increase_stat(session, "callback_calls")

    return
