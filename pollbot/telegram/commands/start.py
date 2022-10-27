"""The start command handler."""
import time
from typing import Optional
from uuid import UUID

from sqlalchemy.orm.scoping import scoped_session
from telegram.bot import Bot
from telegram.update import Update

from pollbot.config import config
from pollbot.display.poll.compilation import (
    compile_poll_text,
    get_poll_text_and_vote_keyboard,
)
from pollbot.enums import ExpectedInput, ReferenceType, StartAction
from pollbot.helper.stats import increase_stat
from pollbot.helper.text import split_text
from pollbot.i18n import i18n
from pollbot.models import Poll, Reference
from pollbot.models.user import User
from pollbot.poll.vote import init_votes
from pollbot.telegram.keyboard.external import (
    get_external_add_option_keyboard,
    get_external_share_keyboard,
)
from pollbot.telegram.keyboard.user import get_main_keyboard
from pollbot.telegram.session import message_wrapper


@message_wrapper()
def start(
    bot: Bot, update: Update, session: scoped_session, user: User
) -> Optional[str]:
    """Send a start text."""
    # Truncate the /start command
    text = update.message.text[6:].strip()
    user.started = True

    poll = None
    action = None
    try:
        poll_uuid = UUID(text.split("-")[0])
        action = StartAction(int(text.split("-")[1]))

        poll = session.query(Poll).filter(Poll.uuid == poll_uuid).one()
    except:  # noqa E722
        text = ""

    # We got an empty text, just send the start message
    if text == "":
        update.message.chat.send_message(
            i18n.t("misc.start", locale=user.locale),
            parse_mode="markdown",
            reply_markup=get_main_keyboard(user),
            disable_web_page_preview=True,
        )

        return

    if poll is None:
        return "This poll no longer exists."

    if action == StartAction.new_option and poll.allow_new_options:
        # Update the expected input and set the current poll
        user.expected_input = ExpectedInput.new_user_option.name
        user.current_poll = poll
        session.commit()

        update.message.chat.send_message(
            i18n.t("creation.option.first", locale=poll.locale),
            parse_mode="markdown",
            reply_markup=get_external_add_option_keyboard(poll),
        )
    elif action == StartAction.show_results:
        # Get all lines of the poll
        lines = compile_poll_text(session, poll)
        # Now split the text into chunks of max 4000 characters
        chunks = split_text(lines)

        for chunk in chunks:
            message = "\n".join(chunk)
            try:
                update.message.chat.send_message(
                    message,
                    parse_mode="markdown",
                    disable_web_page_preview=True,
                )
            # Retry for Timeout error (happens quite often when sending large messages)
            except TimeoutError:
                time.sleep(2)
                update.message.chat.send_message(
                    message,
                    parse_mode="markdown",
                    disable_web_page_preview=True,
                )
            time.sleep(1)

        update.message.chat.send_message(
            i18n.t("misc.start_after_results", locale=poll.locale),
            parse_mode="markdown",
            reply_markup=get_main_keyboard(user),
        )
        increase_stat(session, "show_results")

    elif action == StartAction.share_poll and poll.allow_sharing:
        update.message.chat.send_message(
            i18n.t("external.share_poll", locale=poll.locale),
            reply_markup=get_external_share_keyboard(poll),
        )
        increase_stat(session, "externally_shared")

    elif action == StartAction.vote:
        if not config["telegram"]["allow_private_vote"] and not poll.is_priority():
            return

        if poll.is_priority():
            init_votes(session, poll, user)
            session.commit()

        text, keyboard = get_poll_text_and_vote_keyboard(
            session,
            poll,
            user=user,
        )

        sent_message = update.message.chat.send_message(
            text,
            reply_markup=keyboard,
            parse_mode="markdown",
            disable_web_page_preview=True,
        )

        reference = Reference(
            poll,
            ReferenceType.private_vote.name,
            user=user,
            message_id=sent_message.message_id,
        )
        session.add(reference)
        session.commit()
