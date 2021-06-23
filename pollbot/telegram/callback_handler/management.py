"""Callback functions needed during creation of a Poll."""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm.scoping import scoped_session

from pollbot.decorators import poll_required
from pollbot.display.poll.compilation import get_poll_text
from pollbot.enums import PollDeletionMode
from pollbot.i18n import i18n
from pollbot.models.poll import Poll
from pollbot.poll.helper import clone_poll as clone_poll_internal
from pollbot.poll.update import update_poll_messages
from pollbot.telegram.callback_handler.context import CallbackContext
from pollbot.telegram.keyboard.management import get_management_keyboard


@poll_required
def delete_poll(session: scoped_session, context: CallbackContext, poll: Poll) -> str:

    """Permanently delete the poll."""
    poll.delete = PollDeletionMode.DB_ONLY.name
    session.commit()

    return i18n.t("callback.deleted", locale=context.user.locale)


@poll_required
def delete_poll_with_messages(
    session: scoped_session, context: CallbackContext, poll: Poll
) -> str:

    """Permanently delete the poll."""
    poll.delete = PollDeletionMode.WITH_MESSAGES.name
    session.commit()

    return i18n.t("callback.deleted", locale=context.user.locale)


@poll_required
def close_poll(session: scoped_session, context: CallbackContext, poll: Poll) -> str:

    """Close this poll."""
    poll.closed = True
    session.commit()
    update_poll_messages(
        session, context.bot, poll, context.query.message.message_id, poll.user
    )

    return i18n.t("callback.closed", locale=poll.user.locale)


@poll_required
def reopen_poll(
    session: scoped_session, context: CallbackContext, poll: Poll
) -> Optional[str]:

    """Reopen this poll."""
    if not poll.results_visible:
        return i18n.t("callback.cannot_reopen", locale=poll.user.locale)
    poll.closed = False

    # Remove the due date if it's in the past
    # If the due date is still valid, recalculate the next_notification date
    if poll.due_date is not None and poll.due_date <= datetime.now():
        poll.due_date = None
        poll.next_notification = None
    else:
        poll.set_due_date(poll.due_date)

    session.commit()
    update_poll_messages(
        session, context.bot, poll, context.query.message.message_id, poll.user
    )


@poll_required
def reset_poll(session: scoped_session, context: CallbackContext, poll: Poll) -> str:

    """Reset this poll."""
    for vote in poll.votes:
        session.delete(vote)
    session.commit()

    update_poll_messages(
        session, context.bot, poll, context.query.message.message_id, poll.user
    )
    return i18n.t("callback.votes_removed", locale=poll.user.locale)


@poll_required
def clone_poll(session: scoped_session, context: CallbackContext, poll: Poll) -> str:
    """Clone this poll."""
    new_poll = clone_poll_internal(session, poll)
    session.commit()

    context.tg_chat.send_message(
        get_poll_text(session, new_poll),
        parse_mode="markdown",
        reply_markup=get_management_keyboard(new_poll),
        disable_web_page_preview=True,
    )

    return i18n.t("callback.cloned", locale=poll.user.locale)
