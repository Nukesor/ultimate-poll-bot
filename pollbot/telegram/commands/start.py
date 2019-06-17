"""The start command handler."""
from pollbot.helper.session import session_wrapper
from pollbot.telegram.keyboard import get_main_keyboard
from pollbot.helper import start_text
from pollbot.helper.enums import ExpectedInput
from pollbot.models import Poll


@session_wrapper()
def start(bot, update, session, user):
    """Send a start text."""
    # Truncate the /start command
    text = update.message.text[6:].strip()

    try:
        poll = session.query(Poll).filter(Poll.uuid == text).one()
    except:
        text = ''

    # We got an empty text, just send the start message
    if text == '':
        keyboard = get_main_keyboard()
        update.message.chat.send_message(start_text, parse_mode='Markdown', reply_markup=keyboard)

        return

    poll = session.query(Poll).filter(Poll.uuid == text).one()
    if poll is None:
        return 'This poll no longer exists.'

    user.expected_input = ExpectedInput.new_user_option.name
    user.current_poll = poll
    session.commit()
    return 'Send me the option name (Or send multiple options at once, each option on a new line)'
