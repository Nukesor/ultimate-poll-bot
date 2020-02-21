from telethon import events

from pollbot.client import client
from pollbot.helper.session import message_wrapper
from pollbot.display.settings import get_user_settings_text
from pollbot.telegram.keyboard import (
    get_user_settings_keyboard,
)


@client.on(events.NewMessage(incoming=True, pattern='/settings'))
@message_wrapper(private=True)
async def open_user_settings_command(event, session, user):
    """Open the settings menu for the user."""
    await event.respond(
        get_user_settings_text(user),
        buttons=get_user_settings_keyboard(user),
    )
    raise events.StopPropagation
