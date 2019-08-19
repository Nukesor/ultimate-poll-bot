"""User related keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.i18n import supported_languages, i18n
from pollbot.helper.enums import CallbackType


def get_user_language_keyboard(user):
    """Get user language picker keyboard."""
    buttons = []
    # Compile the possible options for user sorting
    for language in supported_languages:
        button = InlineKeyboardButton(
            language,
            callback_data=f'{CallbackType.user_change_language.value}:{user.id}:{language}'
        )
        buttons.append([button])

    github_url = 'https://github.com/Nukesor/ultimate-poll-bot/tree/master/i18n'
    new_language = i18n.t('keyboard.add_new_language', locale=user.locale)
    buttons.append([InlineKeyboardButton(text=new_language, url=github_url)])

    return InlineKeyboardMarkup(buttons)
