"""Handle inline query results."""
from telegram.ext import run_async

from pollbot.helper.enums import ReferenceType
from pollbot.helper.update import update_reference
from pollbot.helper.session import inline_result_wrapper
from pollbot.models import Poll, Reference


@run_async
@inline_result_wrapper
def handle_chosen_inline_result(bot, update, session, user):
    """Save the chosen inline result."""
    result = update.chosen_inline_result
    poll_id = result.result_id

    poll = session.query(Poll).get(poll_id)

    reference = Reference(
        poll, ReferenceType.inline.name, inline_message_id=result.inline_message_id,
    )
    session.add(reference)
    session.commit()

    update_reference(session, bot, poll, reference)
