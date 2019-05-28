"""Reply keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
)

from pollbot.helper.enums import CallbackType, CallbackResult
from pollbot.helper.enums import PollType, poll_type_translation


def get_main_keyboard():
    """Get the main keyboard for the current user."""
    buttons = [
        ['/donations', '/help'],
        ['/show_active', '/create'],
    ]
    keyboard = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
    return keyboard


def get_init_keyboard(poll):
    """Get the initial inline keyboard for poll creation."""
    change_type = CallbackType.show_poll_type_keyboard.value
    change_type_payload = f"{change_type}:{poll.id}:0"
    change_type_text = "Change poll type"

    toggle_anonymity = CallbackType.toggle_anonymity.value
    toggle_anonymity_payload = f"{toggle_anonymity}:{poll.id}:0"
    toggle_anonymity_text = "Display names in poll" if poll.anonymous else "Anonymize poll"

    buttons = [
        [InlineKeyboardButton(text=change_type_text, callback_data=change_type_payload)],
        [InlineKeyboardButton(text=toggle_anonymity_text, callback_data=toggle_anonymity_payload)],
    ]

    return InlineKeyboardMarkup(buttons)


def get_change_poll_type_keyboard(poll):
    """Get the inline keyboard for changing the poll type."""
    change_type = CallbackType["change_poll_type"].value

    # Dynamically create a button for each poll type
    buttons = []
    for poll_type in PollType:
        text = poll_type_translation[poll_type.name]
        payload = f'{change_type}:{poll.id}:{poll_type.value}'
        button = [InlineKeyboardButton(text=text, callback_data=payload)]
        buttons.append(button)

    return InlineKeyboardMarkup(buttons)


def get_options_entered_keyboard(poll):
    """Get the done keyboard for options during poll creation."""
    options_entered = CallbackType.all_options_entered.value
    payload = f'{options_entered}:{poll.id}:0'
    buttons = [[InlineKeyboardButton(text='Done', callback_data=payload)]]

    return InlineKeyboardMarkup(buttons)


def get_vote_keyboard(poll):
    """Get the keyboard for actual voting."""
    vote_type = CallbackType.vote.value

    buttons = []
    for option in poll.options:
        result = CallbackResult.vote.value
        payload = f'{vote_type}:{option.id}:{result}'

        text = f'{option.name} ({len(option.votes)} votes)'
        buttons.append([InlineKeyboardButton(text=text, callback_data=payload)])

    return InlineKeyboardMarkup(buttons)
