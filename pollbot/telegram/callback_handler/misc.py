"""Option for setting the current date of the picker."""
from pollbot.helper.display.misc import get_help_text_and_keyboard


def switch_help(session, context):
    """Show to vote type keyboard."""
    user = context.user
    text, keyboard = get_help_text_and_keyboard(user, context.action)

    context.query.message.edit_text(
        text,
        parse_mode='Markdown',
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )

    context.query.answer()
