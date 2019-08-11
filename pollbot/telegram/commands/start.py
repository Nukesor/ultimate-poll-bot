"""The start command handler."""
from uuid import UUID
from pollbot.i18n import i18n
from pollbot.helper.enums import ExpectedInput, StartAction
from pollbot.helper.session import session_wrapper
from pollbot.models import Poll
from pollbot.telegram.keyboard import get_main_keyboard
from pollbot.telegram.keyboard.external import get_external_add_option_keyboard


@session_wrapper()
def start(bot, update, session, user):
    """Send a start text."""
    # Truncate the /start command
    text = update.message.text[6:].strip()
    user.started = True

    try:
        poll_uuid = UUID(text.split('-')[0])
        action = StartAction(int(text.split('-')[1]))

        poll = session.query(Poll).filter(Poll.uuid == poll_uuid).one()
    except:
        text = ''

    # We got an empty text, just send the start message
    if text == '':
        keyboard = get_main_keyboard()
        update.message.chat.send_message(
            i18n.t('misc.start', locale=user.locale),
            parse_mode='markdown',
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )

        return

    if poll is None:
        return 'This poll no longer exists.'

    # Update the expected input and set the current poll
    user.expected_input = ExpectedInput.new_user_option.name
    user.current_poll = poll
    session.commit()

    update.message.chat.send_message(
        i18n.t('creation.option.first', locale=poll.locale),
        parse_mode='markdown',
        reply_markup=get_external_add_option_keyboard(poll)
    )
