"""The start command handler."""
import time
from uuid import UUID
from telethon import events

from pollbot.i18n import i18n
from pollbot.client import client
from pollbot.models import Poll, Reference
from pollbot.display.poll.compilation import (
    get_poll_text_and_vote_keyboard,
    compile_poll_text
)
from pollbot.helper.enums import ExpectedInput, StartAction
from pollbot.helper.session import message_wrapper
from pollbot.helper.text import split_text
from pollbot.helper.stats import increase_stat
from pollbot.telegram.keyboard import get_main_keyboard
from pollbot.telegram.keyboard.external import (
    get_external_add_option_keyboard,
    get_external_share_keyboard,
)


@client.on(events.NewMessage(incoming=True, pattern='/start.*'))
@message_wrapper(private=True)
async def start(event, session, user):
    """Send a start text."""
    # Truncate the /start command
    text = ""
    text = event.text[6:].strip()
    user.started = True

    try:
        poll_uuid = UUID(text.split('-')[0])
        action = StartAction(int(text.split('-')[1]))

        poll = session.query(Poll).filter(Poll.uuid == poll_uuid).one()
    except:
        text = ''

    # We got an empty text, just send the start message
    if text == '':
        await event.respond(
            i18n.t('misc.start', locale=user.locale),
            buttons=get_main_keyboard(user),
            link_preview=False,
        )

        raise events.StopPropagation

    if poll is None:
        await event.respond('This poll no longer exists.')
        raise events.StopPropagation

    if action == StartAction.new_option:
        # Update the expected input and set the current poll
        user.expected_input = ExpectedInput.new_user_option.name
        user.current_poll = poll
        session.commit()

        await event.respond(
            i18n.t('creation.option.first', locale=poll.locale),
            buttons=get_external_add_option_keyboard(poll)
        )
    elif action == StartAction.show_results:
        # Get all lines of the poll
        lines = compile_poll_text(session, poll)
        # Now split the text into chunks of max 4000 characters
        chunks = split_text(lines)

        for chunk in chunks:
            message = '\n'.join(chunk)
            try:
                await event.respond(message, link_preview=False)
            # Retry for Timeout error (happens quite often when sending large messages)
            except TimeoutError:
                time.sleep(2)
                await event.respond(message, link_preview=False)
            time.sleep(1)

        await event.respond(
            i18n.t('misc.start_after_results', locale=poll.locale),
            buttons=get_main_keyboard(user),
        )
        increase_stat(session, 'show_results')

    elif action == StartAction.share_poll:
        await event.respond(
            i18n.t('external.share_poll', locale=poll.locale),
            buttons=get_external_share_keyboard(poll)
        )
        increase_stat(session, 'externally_shared')

    elif action == StartAction.vote:
        if poll.is_priority():
            poll.init_votes(session, user)
            session.commit()

        text, keyboard = get_poll_text_and_vote_keyboard(
            session,
            poll,
            user=user,
        )

        sent_message = await event.respond(text, buttons=keyboard, link_preview=False)

        reference = Reference(
            poll,
            vote_user=user,
            vote_message_id=sent_message.message_id,
        )
        session.add(reference)

        session.commit()

    raise events.StopPropagation
