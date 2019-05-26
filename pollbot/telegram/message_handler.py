"""Handle messages."""
from pollbot.helper.session import session_wrapper
from pollbot.helper.enums import PollCreationStep
from pollbot.helper.poll_creation import init_description, init_options, next_option
from pollbot.models import PollOption


@session_wrapper()
def handle_private_text(bot, update, session, user):
    """Read all private messages and the creation of polls."""
    # The user is currently not creating a poll. Just ignore it
    if user.current_poll is None:
        return

    text = update.message.text
    poll = user.current_poll
    chat = update.message.chat
    current_step = user.current_poll.creation_step

    # Add the name
    if current_step == PollCreationStep.name.name:
        poll.name = text
        init_description(chat, poll)

    # Add the description
    if current_step == PollCreationStep.description.name:
        poll.description = text
        init_options(chat, poll)

    # Add an option to the poll
    elif current_step == PollCreationStep.options.name:
        poll_option = PollOption(poll, text)
        session.add(poll_option)
        next_option(chat, poll, text)
