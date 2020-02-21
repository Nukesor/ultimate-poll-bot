"""Poll related commands."""
from telethon import events

from pollbot.i18n import i18n
from pollbot.client import client
from pollbot.helper.session import message_wrapper
from pollbot.display.creation import get_init_text
from pollbot.display.misc import get_poll_list
from pollbot.telegram.keyboard import (
    get_cancel_creation_keyboard,
    get_init_keyboard,
)

from pollbot.models import Poll


@client.on(events.NewMessage(incoming=True, pattern='/create'))
@message_wrapper(private=True)
async def create_poll(event, session, user):
    """Create a new poll."""
    # The previous unfinished poll will be removed
    user.started = True
    if user.current_poll is not None and not user.current_poll.created:
        await event.respond(
            i18n.t('creation.already_creating', locale=user.locale),
            buttons=get_cancel_creation_keyboard(user.current_poll))
        raise events.StopPropagation

    poll = Poll.create(user, session)
    text = get_init_text(poll)
    keyboard = get_init_keyboard(poll)

    await event.respond(text, buttons=keyboard, link_preview=False)
    raise events.StopPropagation


@client.on(events.NewMessage(incoming=True, pattern='/list'))
@message_wrapper(private=True)
async def list_polls(event, session, user):
    """Get a list of all active polls."""
    text, keyboard = get_poll_list(session, user)
    await event.respond(text, buttons=keyboard)
    raise events.StopPropagation


@client.on(events.NewMessage(incoming=True, pattern='/list_closed'))
@message_wrapper(private=True)
async def list_closed_polls(event, session, user):
    """Get a list of all closed polls."""
    text, keyboard = get_poll_list(session, user, closed=True)
    await event.respond(text, buttons=keyboard)
    raise events.StopPropagation
