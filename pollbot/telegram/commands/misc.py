"""Misc commands."""
from telethon import events

from pollbot.i18n import i18n
from pollbot.client import client
from pollbot.helper.session import message_wrapper
from pollbot.display.misc import get_help_text_and_keyboard
from pollbot.telegram.keyboard import get_donations_keyboard


@client.on(events.NewMessage(incoming=True, pattern='/help'))
@message_wrapper(private=True)
async def send_help(event, session, user):
    """Send a help text."""
    text, keyboard = get_help_text_and_keyboard(user, 'intro')

    await event.respond(text, buttons=keyboard, link_preview=False)
    raise events.StopPropagation


@client.on(events.NewMessage(incoming=True, pattern='/donations'))
@message_wrapper(private=True)
async def send_donation_text(event, session, user):
    """Send the donation text."""
    await event.respond(
        i18n.t('misc.donation', locale=user.locale),
        buttons=get_donations_keyboard(user),
        link_preview=False
    )
    raise events.StopPropagation
