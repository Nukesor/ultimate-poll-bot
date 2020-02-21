"""Reply keyboards."""
from telethon import Button

from pollbot.i18n import i18n
from pollbot.helper.enums import CallbackType, PollType
from pollbot.helper import translate_poll_type


def get_back_to_init_button(poll):
    """Get the button to go back to the init creation message."""
    back_text = i18n.t('keyboard.back', locale=poll.locale)
    anonymity_payload = f"{CallbackType.back_to_init.value}:{poll.id}:0"
    return Button.inline(back_text, data=anonymity_payload)


def get_init_keyboard(poll):
    """Get the initial inline keyboard for poll creation."""
    locale = poll.user.locale
    change_type = CallbackType.show_poll_type_keyboard.value
    change_type_payload = f"{change_type}:{poll.id}:0"
    change_type_text = i18n.t('creation.keyboard.change', locale=locale)

    anonymity_text = i18n.t('keyboard.anonymity_settings', locale=locale)
    anonymity_payload = f"{CallbackType.anonymity_settings.value}:{poll.id}:0"

    buttons = [
        [Button.inline(change_type_text, data=change_type_payload)],
        [Button.inline(anonymity_text, data=anonymity_payload)],
    ]

    return buttons


def get_init_settings_keyboard(poll):
    """Get the keyboard for initial settings during poll creation."""
    locale = poll.locale

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
        [Button.inline(toggle_anonymity_text, data=toggle_anonymity_payload)],
        [Button.inline(toggle_results_visible_text, data=toggle_results_visible_payload)],
        [get_back_to_init_button(poll)],
    ]

    return buttons


def get_change_poll_type_keyboard(poll):
    """Get the inline keyboard for changing the vote type."""
    change_type = CallbackType["change_poll_type"].value

    # Dynamically create a button for each vote type
    buttons = []
    for poll_type in PollType:
        text = translate_poll_type(poll_type.name, poll.locale)
        payload = f'{change_type}:{poll.id}:{poll_type.value}'
        button = [Button.inline(text, data=payload)]
        buttons.append(button)

    buttons.append([get_back_to_init_button(poll)])

    return buttons


def get_open_datepicker_keyboard(poll):
    """Get the done keyboard for options during poll creation."""
    locale = poll.user.locale
    payload = f'{CallbackType.open_creation_datepicker.value}:{poll.id}:0'
    buttons = [[Button.inline(i18n.t('datepicker.open', locale=locale), data=payload)]]

    return buttons


def get_cancel_creation_keyboard(poll):
    """Get the cancel creation button."""
    locale = poll.user.locale
    payload = f'{CallbackType.cancel_creation.value}:{poll.id}:0'
    buttons = [[Button.inline(i18n.t('creation.cancel', locale=locale), data=payload)]]

    return buttons


def get_skip_description_keyboard(poll):
    """Get the keyboard for skipping the description."""
    locale = poll.user.locale
    payload = f'{CallbackType.skip_description.value}:{poll.id}:0'
    buttons = [[Button.inline(i18n.t('creation.skip_description', locale=locale), data=payload)]]

    return buttons


def get_options_entered_keyboard(poll):
    """Get the done keyboard for options during poll creation."""
    locale = poll.user.locale
    datepicker_payload = f'{CallbackType.open_creation_datepicker.value}:{poll.id}:0'
    done_payload = f'{CallbackType.all_options_entered.value}:{poll.id}:0'
    buttons = [[
        Button.inline(i18n.t('datepicker.open', locale=locale), data=datepicker_payload),
        Button.inline(i18n.t('keyboard.done', locale=locale), data=done_payload),
    ]]

    return buttons
