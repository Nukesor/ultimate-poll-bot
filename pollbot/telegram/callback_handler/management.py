"""Callback functions needed during creation of a Poll."""
from datetime import datetime

from pollbot.i18n import i18n
from pollbot.helper import poll_required
from pollbot.helper.update import remove_poll_messages, update_poll_messages
from pollbot.display.poll.compilation import get_poll_text
from pollbot.telegram.keyboard import get_management_keyboard


@poll_required
async def delete_poll(session, context, event, poll):
    """Permanently delete the poll."""
    await remove_poll_messages(session, poll)
    session.commit()
    session.delete(poll)
    session.commit()

    return i18n.t('callback.deleted', locale=poll.user.locale)


@poll_required
async def delete_poll_with_messages(session, context, event, poll):
    """Permanently delete the poll."""
    await remove_poll_messages(session, poll, remove_all=True)
    session.commit()
    session.delete(poll)
    session.commit()

    return i18n.t('callback.deleted', locale=poll.user.locale)


@poll_required
async def close_poll(session, context, event, poll):
    """Close this poll."""
    poll.closed = True
    session.commit()
    await update_poll_messages(session, poll)

    return i18n.t('callback.closed', locale=poll.user.locale)


@poll_required
async def reopen_poll(session, context, event, poll):
    """Reopen this poll."""
    if not poll.results_visible:
        return i18n.t('callback.cannot_reopen', locale=poll.user.locale)
    poll.closed = False

    # Remove the due date if it's in the past
    # If the due date is still valid, recalculate the next_notification date
    if poll.due_date is not None and poll.due_date <= datetime.now():
        poll.due_date = None
        poll.next_notification = None
    else:
        poll.set_due_date(poll.due_date)

    session.commit()
    await update_poll_messages(session, poll)


@poll_required
async def reset_poll(session, context, event, poll):
    """Reset this poll."""
    for vote in poll.votes:
        session.delete(vote)
    session.commit()
    await update_poll_messages(session, poll)

    return i18n.t('callback.votes_removed', locale=poll.user.locale)


@poll_required
async def clone_poll(session, context, event, poll):
    """Clone this poll."""
    new_poll = poll.clone(session)
    session.commit()

    event.respond(
        get_poll_text(session, new_poll),
        buttons=get_management_keyboard(new_poll),
        link_preview=False,
    )

    return i18n.t('callback.cloned', locale=poll.user.locale)
