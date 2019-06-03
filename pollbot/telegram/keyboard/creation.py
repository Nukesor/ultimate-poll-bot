"""Reply keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.helper.enums import CallbackType
from pollbot.helper.enums import VoteType, VoteTypeTranslation


def get_init_keyboard(poll):
    """Get the initial inline keyboard for poll creation."""
    change_type = CallbackType.show_vote_type_keyboard.value
    change_type_payload = f"{change_type}:{poll.id}:0"
    change_type_text = "Change vote type"

    toggle_anonymity = CallbackType.toggle_anonymity.value
    toggle_anonymity_payload = f"{toggle_anonymity}:{poll.id}:0"
    toggle_anonymity_text = "Display names in poll" if poll.anonymous else "Anonymize poll"

    toggle_results_visible = CallbackType.toggle_results_visible.value
    toggle_results_visible_payload = f"{toggle_results_visible}:{poll.id}:0"
    toggle_results_visible_text = "Hide results until poll is closed" if poll.results_visible else "Permanently show results"

    buttons = [
        [InlineKeyboardButton(text=change_type_text, callback_data=change_type_payload)],
        [InlineKeyboardButton(text=toggle_anonymity_text, callback_data=toggle_anonymity_payload)],
        [InlineKeyboardButton(text=toggle_results_visible_text, callback_data=toggle_results_visible_payload)],
    ]

    return InlineKeyboardMarkup(buttons)


def get_change_vote_type_keyboard(poll):
    """Get the inline keyboard for changing the vote type."""
    change_type = CallbackType["change_vote_type"].value

    # Dynamically create a button for each vote type
    buttons = []
    for vote_type in VoteType:
        text = VoteTypeTranslation[vote_type.name]
        payload = f'{change_type}:{poll.id}:{vote_type.value}'
        button = [InlineKeyboardButton(text=text, callback_data=payload)]
        buttons.append(button)

    return InlineKeyboardMarkup(buttons)


def get_options_entered_keyboard(poll):
    """Get the done keyboard for options during poll creation."""
    options_entered = CallbackType.all_options_entered.value
    payload = f'{options_entered}:{poll.id}:0'
    buttons = [[InlineKeyboardButton(text='Done', callback_data=payload)]]

    return InlineKeyboardMarkup(buttons)
