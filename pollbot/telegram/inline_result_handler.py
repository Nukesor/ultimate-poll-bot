"""Handle inline query results."""
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm.scoping import scoped_session
from telegram.bot import Bot
from telegram.update import Update

from pollbot.enums import ReferenceType
from pollbot.helper.stats import increase_user_stat
from pollbot.models import Poll, Reference, User
from pollbot.poll.update import try_update_reference
from pollbot.telegram.session import inline_result_wrapper


@inline_result_wrapper
def handle_chosen_inline_result(
    bot: Bot, update: Update, session: scoped_session, user: User
) -> None:
    """Save the chosen inline result."""
    result = update.chosen_inline_result
    poll_id = result.result_id

    try:
        poll = session.query(Poll).get(poll_id)

    except DataError:
        # Possile if the poll has been shared too often and
        # the inline result is picked despite saying otherwise.
        return

    if result.inline_message_id is None:
        return

    try:
        reference = Reference(
            poll,
            ReferenceType.inline.name,
            inline_message_id=result.inline_message_id,
        )
        session.add(reference)
        session.commit()
    except (UniqueViolation, IntegrityError):
        # I don't know how this can happen, but it happens.
        # It seems that user can spam click inline query results, which then leads
        # to multiple chosen_inline_result queries being sent to the bot.
        session.rollback()
        return

    try_update_reference(session, bot, poll, reference, first_try=True)

    increase_user_stat(session, user, "inline_shares")
