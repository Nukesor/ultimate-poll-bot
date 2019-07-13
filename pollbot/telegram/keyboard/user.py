"""User related keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.helper.enums import CallbackType


def get_user_language_keyboard(user):
    """Get user language picker keyboard."""
    buttons = []
    # Compile the possible options for user sorting
    for language in ['english']:
        button = InlineKeyboardButton(
            language,
            callback_data=f'{CallbackType.user_change_language.value}:{user.id}:{language}'
        )
        buttons.append([button])

    github_url = 'https://github.com/Nukesor/ultimate-poll-bot/tree/master/i18n'
    buttons.append([InlineKeyboardButton(text='Add a new language', url=github_url)])

    return InlineKeyboardMarkup(buttons)
