"""The start command handler."""
import time
from uuid import UUID
from telegram.ext import run_async

from pollbot.i18n import i18n
from pollbot.models import Poll, Reference
from pollbot.display import (
    compile_poll_text,
    get_poll_text_and_vote_keyboard,
)
from pollbot.helper.enums import ExpectedInput, StartAction
from pollbot.helper.session import session_wrapper
from pollbot.helper.text import split_text
from pollbot.helper.stats import increase_stat
from pollbot.telegram.keyboard import get_main_keyboard
from pollbot.telegram.keyboard.external import (
    get_external_add_option_keyboard,
    get_external_share_keyboard,
)


@run_async
@session_wrapper()
def start(bot, update, session, user):
    """Send a start text."""
    # Truncate the /start command
    text = ""
    if update.message is not None:
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
        update.message.chat.send_message(
            i18n.t('misc.start', locale=user.locale),
            parse_mode='markdown',
            reply_markup=get_main_keyboard(user),
            disable_web_page_preview=True,
        )

        return

    if poll is None:
        return 'This poll no longer exists.'

    if action == StartAction.new_option:
        # Update the expected input and set the current poll
        user.expected_input = ExpectedInput.new_user_option.name
        user.current_poll = poll
        session.commit()

        update.message.chat.send_message(
            i18n.t('creation.option.first', locale=poll.locale),
            parse_mode='markdown',
            reply_markup=get_external_add_option_keyboard(poll)
        )
    elif action == StartAction.show_results:
        # Get all lines of the poll
        lines = compile_poll_text(session, poll)
        # Now split the text into chunks of max 4000 characters
        chunks = split_text(lines)

        for chunk in chunks:
            message = '\n'.join(chunk)
            try:
                update.message.chat.send_message(
                    message,
                    parse_mode='markdown',
                    disable_web_page_preview=True,
                )
            # Retry for Timeout error (happens quite often when sending large messages)
            except TimeoutError:
                time.sleep(2)
                update.message.chat.send_message(
                    message,
                    parse_mode='markdown',
                    disable_web_page_preview=True,
                )
            time.sleep(1)

        update.message.chat.send_message(
            i18n.t('misc.start_after_results', locale=poll.locale),
            parse_mode='markdown',
            reply_markup=get_main_keyboard(user),
        )
        increase_stat(session, 'show_results')

    elif action == StartAction.share_poll:
        update.message.chat.send_message(
            i18n.t('external.share_poll', locale=poll.locale),
            reply_markup=get_external_share_keyboard(poll)
        )
        increase_stat(session, 'externally_shared')
    elif action == StartAction.vote:
        text, keyboard = get_poll_text_and_vote_keyboard(
            session,
            poll,
            user=user,
        )

        sent_message = update.message.chat.send_message(
            text,
            reply_markup=keyboard,
            parse_mode='markdown',
            disable_web_page_preview=True,
        )

        reference = Reference(
            poll,
            vote_user=user,
            vote_message_id=sent_message.message_id,
        )
        session.add(reference)
        session.commit()
