"""Handle messages."""
from pollbot.helper.session import session_wrapper
from pollbot.helper.enums import ExpectedInput
from pollbot.helper.creation import next_option
from pollbot.models import PollOption


@session_wrapper()
def handle_private_text(bot, update, session, user):
    """Read all private messages and the creation of polls."""
    # The user is currently not editing or creating a poll. Just ignore it
    if user.current_poll.expected_input is None:
        return

    text = update.message.text.strip()
    poll = user.current_poll
    chat = update.message.chat
    expected_input = ExpectedInput[user.current_poll.expected_input]

    # Add the name
    if expected_input == ExpectedInput.name:
        poll.name = text
        poll.expected_input = ExpectedInput.description.name
        chat.send_message('Now send me the description')

    # Add the description
    elif expected_input == ExpectedInput.description:
        poll.description = text
        poll.expected_input = ExpectedInput.options.name
        message = 'Now send me the first option (Or send multiple options at once, each option in a new line)'
        chat.send_message(message)

    # Add an option to the poll
    elif expected_input == ExpectedInput.options:
        # Multiple options can be sent at once separated by newline
        # Strip them and ignore empty lines
        options_to_add = [x.strip() for x in text.split('\n') if x.strip() != '']
        added_options = []

        for option_to_add in options_to_add:
            # Ignore options that already exist
            for existing_option in poll.options:
                if existing_option.name == option_to_add and len(options_to_add) == 1:
                    return "There already exists a option with this name. ⚠️"""

                continue

            poll_option = PollOption(poll, option_to_add)
            poll.options.append(poll_option)
            added_options.append(option_to_add)

        if len(added_options) == 0:
            return "No new options have been added. ⚠️"

        next_option(chat, poll, added_options)
