"""Reply keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.helper.enums import CallbackType
from pollbot.helper.enums import VoteType, VoteTypeTranslation
from pollbot.telegram.keyboard.date_picker import get_datepicker_buttons


def get_init_keyboard(poll):
    """Get the initial inline keyboard for poll creation."""
    change_type = CallbackType.show_vote_type_keyboard.value
    change_type_payload = f"{change_type}:{poll.id}:0"
    change_type_text = "Change poll type"

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


def get_open_datepicker_keyboard(poll):
    """Get the done keyboard for options during poll creation."""
    payload = f'{CallbackType.open_creation_datepicker.value}:{poll.id}:0'
    buttons = [[InlineKeyboardButton(text='Open Datepicker', callback_data=payload)]]

    return InlineKeyboardMarkup(buttons)


def get_cancel_creation_keyboard(poll):
    """Get the cancel creation button."""
    payload = f'{CallbackType.cancel_creation.value}:{poll.id}:0'
    buttons = [[InlineKeyboardButton(text='Cancel previous creation', callback_data=payload)]]

    return InlineKeyboardMarkup(buttons)


def get_skip_description_keyboard(poll):
    """Get the keyboard for skipping the description."""
    payload = f'{CallbackType.skip_description.value}:{poll.id}:0'
    buttons = [[InlineKeyboardButton(text='Skip Description', callback_data=payload)]]

    return InlineKeyboardMarkup(buttons)


def get_options_entered_keyboard(poll):
    """Get the done keyboard for options during poll creation."""
    datepicker_payload = f'{CallbackType.open_creation_datepicker.value}:{poll.id}:0'
    done_payload = f'{CallbackType.all_options_entered.value}:{poll.id}:0'
    buttons = [[
        InlineKeyboardButton(text='Open Datepicker', callback_data=datepicker_payload),
        InlineKeyboardButton(text='Done', callback_data=done_payload),
    ]]

    return InlineKeyboardMarkup(buttons)


def get_creation_datepicker_keyboard(poll):
    """Get the done keyboard for options during poll creation."""
    datepicker_buttons = get_datepicker_buttons(poll)

    # Create back and done buttons
    close_payload = f'{CallbackType.close_creation_datepicker.value}:{poll.id}:0'
    buttons = [InlineKeyboardButton(text='Close', callback_data=close_payload)]
    if len(poll.options) > 0:
        done_payload = f'{CallbackType.all_options_entered.value}:{poll.id}:0'
        buttons.append(InlineKeyboardButton(text='Done', callback_data=done_payload))
    datepicker_buttons.append(buttons)

    # Create pick button
    pick_payload = f'{CallbackType.pick_date_option.value}:{poll.id}:0'
    datepicker_buttons.append([InlineKeyboardButton(text='Pick this date', callback_data=pick_payload)])

    return InlineKeyboardMarkup(datepicker_buttons)
