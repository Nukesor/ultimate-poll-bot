"""Option for setting the current date of the picker."""
from pollbot.models import PollOption
from pollbot.display.misc import get_help_text_and_keyboard


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


def show_option_name(session, context):
    """Return the option name via callback query."""
    option = session.query(PollOption).get(context.action)

    if option is None:
        context.query.answer("Option no longer exists")

    message = option.name
    if len(message) > 190:
        message = message[0:190]

    if option.is_date:
        message = option.get_formatted_name()

    context.query.answer(message)
