"""Reply keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.i18n import i18n
from pollbot.helper.enums import CallbackType, PollType
from pollbot.helper import translate_poll_type
from pollbot.telegram.keyboard.date_picker import get_datepicker_buttons


def get_init_keyboard(poll):
    """Get the initial inline keyboard for poll creation."""
    locale = poll.user.locale
    change_type = CallbackType.show_poll_type_keyboard.value
    change_type_payload = f"{change_type}:{poll.id}:0"
    change_type_text = i18n.t('creation.keyboard.change', locale=locale)

    toggle_anonymity = CallbackType.toggle_anonymity.value
    toggle_anonymity_payload = f"{toggle_anonymity}:{poll.id}:0"
    toggle_anonymity_text = i18n.t('creation.keyboard.anonymity', locale=locale)
    if poll.anonymous:
        toggle_anonymity_text = i18n.t('creation.keyboard.no_anonymity', locale=locale)

    toggle_results_visible = CallbackType.toggle_results_visible.value
    toggle_results_visible_payload = f"{toggle_results_visible}:{poll.id}:0"
    toggle_results_visible_text = i18n.t('creation.keyboard.results_visible', locale=locale)
    if poll.results_visible:
        toggle_results_visible_text = i18n.t('creation.keyboard.results_not_visible', locale=locale)

    buttons = [
        [InlineKeyboardButton(change_type_text, callback_data=change_type_payload)],
        [InlineKeyboardButton(toggle_anonymity_text, callback_data=toggle_anonymity_payload)],
        [InlineKeyboardButton(toggle_results_visible_text, callback_data=toggle_results_visible_payload)],
    ]

    return InlineKeyboardMarkup(buttons)


def get_change_poll_type_keyboard(poll):
    """Get the inline keyboard for changing the vote type."""
    change_type = CallbackType["change_poll_type"].value

    # Dynamically create a button for each vote type
    buttons = []
    for poll_type in PollType:
        text = translate_poll_type(poll_type.name, poll.locale)
        payload = f'{change_type}:{poll.id}:{poll_type.value}'
        button = [InlineKeyboardButton(text, callback_data=payload)]
        buttons.append(button)

    return InlineKeyboardMarkup(buttons)


def get_open_datepicker_keyboard(poll):
    """Get the done keyboard for options during poll creation."""
    payload = f'{CallbackType.open_creation_datepicker.value}:{poll.id}:0'
    buttons = [[InlineKeyboardButton(
        i18n.t('datepicker.open', locale=poll.user.locale),
        callback_data=payload,
    )]]

    return InlineKeyboardMarkup(buttons)


def get_cancel_creation_keyboard(poll):
    """Get the cancel creation button."""
    payload = f'{CallbackType.cancel_creation.value}:{poll.id}:0'
    buttons = [[InlineKeyboardButton(
        i18n.t('creation.cancel', locale=poll.user.locale),
        callback_data=payload)]]

    return InlineKeyboardMarkup(buttons)


def get_skip_description_keyboard(poll):
    """Get the keyboard for skipping the description."""
    payload = f'{CallbackType.skip_description.value}:{poll.id}:0'
    buttons = [[InlineKeyboardButton(
        i18n.t('creation.skip_description', locale=poll.user.locale),
        callback_data=payload)]]

    return InlineKeyboardMarkup(buttons)


def get_options_entered_keyboard(poll):
    """Get the done keyboard for options during poll creation."""
    locale = poll.user.locale
    datepicker_payload = f'{CallbackType.open_creation_datepicker.value}:{poll.id}:0'
    done_payload = f'{CallbackType.all_options_entered.value}:{poll.id}:0'
    buttons = [[
        InlineKeyboardButton(i18n.t('datepicker.open', locale=locale),
                             callback_data=datepicker_payload),
        InlineKeyboardButton(i18n.t('keyboard.done', locale=locale),
                             callback_data=done_payload),
    ]]

    return InlineKeyboardMarkup(buttons)


def get_creation_datepicker_keyboard(poll):
    """Get the done keyboard for options during poll creation."""
    locale = poll.user.locale
    datepicker_buttons = get_datepicker_buttons(poll)

    # Create back and done buttons
    close_payload = f'{CallbackType.close_creation_datepicker.value}:{poll.id}:0'
    buttons = [InlineKeyboardButton(i18n.t('keyboard.close', locale=locale),
                                    callback_data=close_payload)]
    if len(poll.options) > 0:
        done_payload = f'{CallbackType.all_options_entered.value}:{poll.id}:0'
        buttons.append(InlineKeyboardButton(i18n.t('keyboard.done', locale=locale),
                                            callback_data=done_payload))
    datepicker_buttons.append(buttons)

    # Create pick button
    pick_payload = f'{CallbackType.pick_date_option.value}:{poll.id}:0'
    datepicker_buttons.append([InlineKeyboardButton(i18n.t('datepicker.pick_date', locale=locale),
                                                    callback_data=pick_payload)])

    return InlineKeyboardMarkup(datepicker_buttons)
