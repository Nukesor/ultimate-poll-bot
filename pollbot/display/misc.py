"""Display helper for misc stuff."""
from pollbot.i18n import i18n
from pollbot.telegram.keyboard.misc import get_help_keyboard


def get_help_text_and_keyboard(user, current_category):
    """Create the help message depending on the currently selected help category."""
    categories = [
        'creation',
        'settings',
        'notifications',
        'management',
        'languages',
        'bugs',
    ]

    text = i18n.t(f'misc.help.{current_category}', locale=user.locale)
    keyboard = get_help_keyboard(user, categories, current_category)

    return text, keyboard
