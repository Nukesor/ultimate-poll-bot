"""Reply keyboards."""
from telethon import Button

from pollbot.i18n import i18n
from pollbot.helper.enums import CallbackType, CallbackResult


def get_back_to_management_button(poll):
    """Get the back to management menu button for management sub menus."""
    locale = poll.user.locale
    payload = f'{CallbackType.menu_back.value}:{poll.id}:{CallbackResult.main_menu.value}'
    return Button.inline(i18n.t('keyboard.back', locale=locale), data=payload)


def get_management_keyboard(poll):
    """Get the management keyboard for this poll."""
    locale = poll.user.locale
    delete_payload = f'{CallbackType.menu_delete.value}:{poll.id}:0'

    if poll.closed and not poll.results_visible:
        return [[Button.inline(
            i18n.t('keyboard.delete', locale=locale),
            data=delete_payload)]]
    elif poll.closed:
        reopen_payload = f'{CallbackType.reopen.value}:{poll.id}:0'
        reset_payload = f'{CallbackType.reset.value}:{poll.id}:0'
        clone_payload = f'{CallbackType.clone.value}:{poll.id}:0'
        buttons = [
            [
                Button.inline(i18n.t('keyboard.reset', locale=locale), data=reset_payload),
                Button.inline(i18n.t('keyboard.clone', locale=locale), data=clone_payload),
            ],
            [
                Button.inline(i18n.t('keyboard.delete', locale=locale), data=delete_payload),
                Button.switch_inline(i18n.t('keyboard.share', locale=locale), query=f'{poll.name} closed_polls'),
            ],
            [Button.inline(
                i18n.t('keyboard.reopen', locale=locale),
                data=reopen_payload)]
        ]
        return buttons

    vote_payload = f'{CallbackType.menu_vote.value}:{poll.id}:0'
    option_payload = f'{CallbackType.menu_option.value}:{poll.id}:0'
    delete_payload = f'{CallbackType.menu_delete.value}:{poll.id}:0'

    if poll.results_visible:
        close_payload = f'{CallbackType.close.value}:{poll.id}:0'
    else:
        close_payload = f'{CallbackType.menu_close.value}:{poll.id}:0'

    buttons = [
        [
            Button.switch_inline(i18n.t('keyboard.share', locale=locale), query=poll.name),
        ],
        [
            Button.inline(i18n.t('keyboard.vote', locale=locale), data=vote_payload),
            Button.inline(i18n.t('keyboard.settings', locale=locale), data=option_payload),
        ],
        [
            Button.inline(i18n.t('keyboard.delete', locale=locale), data=delete_payload),
            Button.inline(i18n.t('keyboard.close_poll', locale=locale), data=close_payload),
        ],
    ]

    return buttons


def get_close_confirmation(poll):
    """Get the confirmation keyboard for closing of a poll."""
    payload = f'{CallbackType.close.value}:{poll.id}:0'
    locale = poll.user.locale
    buttons = [
        [Button.inline(
            i18n.t('keyboard.permanently_close', locale=locale),
            data=payload)],
        [get_back_to_management_button(poll)],
    ]
    return buttons


def get_deletion_confirmation(poll):
    """Get the confirmation keyboard for poll deletion."""
    delete_payload = f'{CallbackType.delete.value}:{poll.id}:0'
    delete_all_payload = f'{CallbackType.delete_poll_with_messages.value}:{poll.id}:0'
    locale = poll.user.locale
    buttons = [
        [Button.inline(
            i18n.t('keyboard.permanently_delete', locale=locale),
            data=delete_payload)],
        [Button.inline(
            i18n.t('keyboard.permanently_delete_with_messages', locale=locale),
            data=delete_all_payload)],
        [get_back_to_management_button(poll)],
    ]
    return buttons


def get_poll_list_keyboard(polls):
    """Get the confirmation keyboard for poll deletion."""
    buttons = []
    for poll in polls:
        payload = f'{CallbackType.menu_show.value}:{poll.id}:0'
        buttons.append([Button.inline(poll.name, data=payload)])

    return buttons
