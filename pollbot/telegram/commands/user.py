from telethon import events

from pollbot.helper.session import message_wrapper
from pollbot.display.settings import get_user_settings_text
from pollbot.telegram.keyboard import (
    get_user_settings_keyboard,
)


@client.on(events.NewMessage(incoming=True, pattern='/reset_broadcast'))
@message_wrapper(private=True)
def open_user_settings_command(event, session, user):
    """Open the settings menu for the user."""
    event.respond(
        get_user_settings_text(user),
        reply_markup=get_user_settings_keyboard(user),
        parse_mode='markdown',
    )
