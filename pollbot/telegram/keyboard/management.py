"""Reply keyboards."""
from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from pollbot.config import config
from pollbot.enums import CallbackResult, CallbackType, StartAction
from pollbot.i18n import i18n
from pollbot.models.poll import Poll
from pollbot.telegram.keyboard.helper import get_start_button_payload


def get_back_to_management_button(poll: Poll) -> InlineKeyboardButton:
    """Get the back to management menu button for management sub menus."""
    locale = poll.user.locale
    payload = (
        f"{CallbackType.menu_back.value}:{poll.id}:{CallbackResult.main_menu.value}"
    )
    return InlineKeyboardButton(
        i18n.t("keyboard.back", locale=locale), callback_data=payload
    )


def get_management_keyboard(poll: Poll) -> InlineKeyboardMarkup:
    """Get the management keyboard for this poll."""
    locale = poll.user.locale
    delete_payload = f"{CallbackType.menu_delete.value}:{poll.id}:0"

    if poll.closed:
        reopen_payload = f"{CallbackType.reopen.value}:{poll.id}:0"
        reset_payload = f"{CallbackType.reset.value}:{poll.id}:0"
        clone_payload = f"{CallbackType.clone.value}:{poll.id}:0"
        buttons = []

        if poll.summarize or poll.permanently_summarized:
            payload = get_start_button_payload(poll, StartAction.show_results)
            bot_name = config["telegram"]["bot_name"]
            url = f"http://t.me/{bot_name}?start={payload}"
            row = [
                InlineKeyboardButton(
                    i18n.t("keyboard.show_results", locale=poll.locale), url=url
                )
            ]
            buttons.append(row)

        buttons.append(
            [
                InlineKeyboardButton(
                    i18n.t("keyboard.clone", locale=locale), callback_data=clone_payload
                ),
                InlineKeyboardButton(
                    i18n.t("keyboard.delete", locale=locale),
                    callback_data=delete_payload,
                ),
            ]
        )
        row = [
            InlineKeyboardButton(
                i18n.t("keyboard.share", locale=locale),
                switch_inline_query=f"{poll.name} closed_polls",
            ),
        ]

        # Only allow the poll to reset on non-directly visible polls
        if poll.results_visible:
            row.insert(
                0,
                InlineKeyboardButton(
                    i18n.t("keyboard.reset", locale=locale),
                    callback_data=reset_payload,
                ),
            )

        buttons.append(row)

        # Only allow to re-open if the settings allows so.
        if poll.results_visible:
            buttons.append(
                [
                    InlineKeyboardButton(
                        i18n.t("keyboard.reopen", locale=locale),
                        callback_data=reopen_payload,
                    )
                ]
            )

        return InlineKeyboardMarkup(buttons)

    vote_payload = f"{CallbackType.menu_vote.value}:{poll.id}:0"
    option_payload = f"{CallbackType.menu_option.value}:{poll.id}:0"
    delete_payload = f"{CallbackType.menu_delete.value}:{poll.id}:0"

    if poll.results_visible:
        close_payload = f"{CallbackType.close.value}:{poll.id}:0"
    else:
        close_payload = f"{CallbackType.menu_close.value}:{poll.id}:0"

    buttons = [
        [
            InlineKeyboardButton(
                i18n.t("keyboard.share", locale=locale), switch_inline_query=poll.name
            ),
        ],
        [
            InlineKeyboardButton(
                i18n.t("keyboard.vote", locale=locale), callback_data=vote_payload
            ),
            InlineKeyboardButton(
                i18n.t("keyboard.settings", locale=locale), callback_data=option_payload
            ),
        ],
        [
            InlineKeyboardButton(
                i18n.t("keyboard.delete", locale=locale), callback_data=delete_payload
            ),
            InlineKeyboardButton(
                i18n.t("keyboard.close_poll", locale=locale),
                callback_data=close_payload,
            ),
        ],
    ]

    return InlineKeyboardMarkup(buttons)


def get_close_confirmation(poll: Poll) -> InlineKeyboardMarkup:
    """Get the confirmation keyboard for closing of a poll."""
    payload = f"{CallbackType.close.value}:{poll.id}:0"
    locale = poll.user.locale
    buttons = [
        [
            InlineKeyboardButton(
                i18n.t("keyboard.permanently_close", locale=locale),
                callback_data=payload,
            )
        ],
        [get_back_to_management_button(poll)],
    ]
    return InlineKeyboardMarkup(buttons)


def get_deletion_confirmation(poll: Poll) -> InlineKeyboardMarkup:
    """Get the confirmation keyboard for poll deletion."""
    delete_payload = f"{CallbackType.delete.value}:{poll.id}:0"
    delete_all_payload = f"{CallbackType.delete_poll_with_messages.value}:{poll.id}:0"
    locale = poll.user.locale
    buttons = [
        [
            InlineKeyboardButton(
                i18n.t("keyboard.permanently_delete", locale=locale),
                callback_data=delete_payload,
            )
        ],
        [
            InlineKeyboardButton(
                i18n.t("keyboard.permanently_delete_with_messages", locale=locale),
                callback_data=delete_all_payload,
            )
        ],
        [get_back_to_management_button(poll)],
    ]
    return InlineKeyboardMarkup(buttons)


def get_poll_list_keyboard(
    polls: List[Poll], closed: bool, offset: int, poll_count: int
) -> InlineKeyboardMarkup:
    """Get the confirmation keyboard for poll deletion."""
    buttons = []
    for poll in polls:
        payload = f"{CallbackType.menu_show.value}:{poll.id}:0"
        text = poll.name
        if len(text) > 40:
            text = poll.name[0:40]
        buttons.append([InlineKeyboardButton(text, callback_data=payload)])

    # Add navigation
    navigation = []
    if closed:
        callback_type = CallbackType.user_list_closed_polls_navigation.value
    else:
        callback_type = CallbackType.user_list_polls_navigation.value

    # Only show the previous button, if we aren't on the first page
    if offset > 0:
        previous_page = f"{callback_type}:{offset-10}:0"
        navigation.append(InlineKeyboardButton("<", callback_data=previous_page))

    # Only show the next button, if there's a next page
    if poll_count > offset + 10:
        next_page = f"{callback_type}:{offset+10}:0"
        navigation.append(InlineKeyboardButton(">", callback_data=next_page))

    if len(navigation) > 0:
        buttons.append(navigation)

    return InlineKeyboardMarkup(buttons)
