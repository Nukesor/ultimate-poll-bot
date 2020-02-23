"""Handle inline query results."""
from telethon import events, types

from pollbot.client import client
from pollbot.models import Poll, Reference
from pollbot.helper.update import update_poll_messages
from pollbot.helper.session import inline_query_wrapper


@client.on(events.Raw(types.UpdateBotInlineSend))
@inline_query_wrapper
async def handle_chosen_inline_result(session, event, user):
    """Save the chosen inline result."""
    poll_id = event.id

    poll = session.query(Poll).get(poll_id)

    reference = Reference(
        poll,
        inline_message_id=event.msg_id.id,
        inline_message_dc_id=event.msg_id.dc_id,
        inline_message_access_hash=event.msg_id.access_hash,
    )
    session.add(reference)
    session.commit()

    await update_poll_messages(session, poll)
