"""All keyboards for external users that don't own the poll."""
from telethon import Button

from pollbot.i18n import i18n
from pollbot.helper.enums import (
    CallbackType,
)


def get_notify_keyboard(polls):
    """Get the keyboard for activationg notifications in a chat."""
    # Add back and pick buttons
    buttons = []
    for poll in polls:
        pick_payload = f'{CallbackType.activate_notification.value}:{poll.id}:0'
        buttons.append([Button.inline(poll.name, data=pick_payload)])

    return buttons


def get_external_add_option_keyboard(poll):
    """Get the external keyboard for adding a new option after poll creation."""
    locale = poll.user.locale
    datepicker_payload = f'{CallbackType.external_open_datepicker.value}:{poll.id}:0'
    cancel_payload = f'{CallbackType.external_cancel.value}:{poll.id}:0'
    buttons = [
        [Button.inline(i18n.t('datepicker.open', locale=locale), data=datepicker_payload)],
        [Button.inline(i18n.t('keyboard.done', locale=poll.locale), data=cancel_payload)],
    ]

    keyboard = buttons

    return keyboard


def get_external_share_keyboard(poll):
    """Allow external users to share a poll."""
    locale = poll.user.locale

    buttons = [
        [Button.inline(i18n.t('keyboard.share', locale=locale), switch_inline_query=str(poll.uuid))]
    ]
    keyboard = buttons

    return keyboard
