"""Option for setting the current date of the picker."""
from sqlalchemy.orm.scoping import scoped_session

from pollbot.display.misc import get_help_text_and_keyboard
from pollbot.models import Option
from pollbot.telegram.callback_handler.context import CallbackContext


def switch_help(_: scoped_session, context: CallbackContext) -> None:
    """Show the correct help section."""
    user = context.user
    text, keyboard = get_help_text_and_keyboard(user, str(context.action))

    context.query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


def show_option_name(session: scoped_session, context: CallbackContext) -> str:
    """Return the option name via callback query."""
    option = session.query(Option).get(context.action)

    if option is None:
        return "Option no longer exists"

    message = option.name
    if len(message) > 190:
        message = message[0:190]

    if option.is_date:
        message = option.get_formatted_name()

    return message


def ignore(_: scoped_session, context: CallbackContext) -> None:
    """Simple generic helper to return a hint on styling buttons."""
    context.query.answer("This button doesn't do anything and is just for styling.")
