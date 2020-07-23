"""Handle inline query results."""
from telegram.ext import run_async
from sqlalchemy.exc import DataError
from psycopg2.errors import UniqueViolation

from pollbot.helper.enums import ReferenceType
from pollbot.helper.stats import increase_user_stat
from pollbot.helper.update import update_reference
from pollbot.helper.session import inline_result_wrapper
from pollbot.models import Poll, Reference


@run_async
@inline_result_wrapper
def handle_chosen_inline_result(bot, update, session, user):
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
            poll, ReferenceType.inline.name, inline_message_id=result.inline_message_id,
        )
        session.add(reference)
        session.commit()
    except UniqueViolation:
        # I don't know how this can happen, but it happens.
        return

    update_reference(session, bot, poll, reference)
    increase_user_stat(session, user, "inline_shares")
