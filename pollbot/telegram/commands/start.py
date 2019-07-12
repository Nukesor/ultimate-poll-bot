"""The start command handler."""
from pollbot.i18n import i18n
from pollbot.helper.enums import ExpectedInput
from pollbot.helper.session import session_wrapper
from pollbot.models import Poll
from pollbot.telegram.keyboard import get_main_keyboard
from pollbot.telegram.keyboard.external import get_external_datepicker_keyboard


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
        update.message.chat.send_message(
            i18n.t('misc.start', locale=user.locale),
            parse_mode='markdown',
            reply_markup=keyboard,
        )

        return

    poll = session.query(Poll).filter(Poll.uuid == text).one()
    if poll is None:
        return 'This poll no longer exists.'

    # Update the expected input and set the current poll
    user.expected_input = ExpectedInput.new_user_option.name
    user.current_poll = poll
    session.commit()

    text = 'Send me the option name (Or send multiple options at once, each option on a new line)'
    update.message.chat.send_message(
        text,
        parse_mode='markdown',
        reply_markup=get_external_datepicker_keyboard(poll)
    )
