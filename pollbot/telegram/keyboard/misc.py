"""All keyboards for external users that don't own the poll."""
from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from pollbot.enums import CallbackType
from pollbot.i18n import i18n
from pollbot.models.user import User
from pollbot.telegram.keyboard.user import get_back_to_menu_button


def get_help_keyboard(
    user: User, categories: List[str], current_category: str
) -> InlineKeyboardMarkup:
    """Get the done keyboard for options during poll creation."""
    rows = []
    current_row = []
    while len(categories) > 0:
        category = categories.pop(0)
        payload = f"{CallbackType.switch_help.value}:0:{category}"
        text = i18n.t(f"keyboard.help.{category}", locale=user.locale)
        if category == current_category:
            text = f"[ {text} ]"
        button = InlineKeyboardButton(text, callback_data=payload)

        if len(current_row) < 3:
            current_row.append(button)
        else:
            rows.append(current_row)
            current_row = [button]

    rows.append(current_row)
    rows.append([get_back_to_menu_button(user)])

    return InlineKeyboardMarkup(rows)
