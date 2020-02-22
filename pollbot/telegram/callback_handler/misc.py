"""Option for setting the current date of the picker."""
from pollbot.models import PollOption
from pollbot.display.misc import get_help_text_and_keyboard


async def switch_help(session, context, event):
    """Show the correct help section."""
    user = context.user
    text, keyboard = get_help_text_and_keyboard(user, context.action)

    await event.edit(text, buttons=keyboard, link_preview=False)


async def show_option_name(session, context, event):
    """Return the option name via callback query."""
    option = session.query(PollOption).get(context.action)

    if option is None:
        return "Option no longer exists"

    message = option.name
    if len(message) > 190:
        message = message[0:190]

    if option.is_date:
        message = option.get_formatted_name()

    return message
