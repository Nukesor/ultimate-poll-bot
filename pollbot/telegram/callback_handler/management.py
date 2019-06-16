"""Callback functions needed during creation of a Poll."""
from pollbot.helper import poll_required
from pollbot.helper.update import remove_poll_messages, update_poll_messages


@poll_required
def delete_poll(session, context, poll):
    """Permanently delete the pall."""
    remove_poll_messages(session, context.bot, poll)
    poll.deleted = True
    session.commit()


@poll_required
def close_poll(session, context, poll):
    """Close this poll."""
    poll.closed = True
    session.commit()
    update_poll_messages(session, context.bot, poll)


@poll_required
def reopen_poll(session, context, poll):
    """Reopen this poll."""
    if not poll.results_visible:
        context.query.answer('This poll cannot be reopened')
        return
    poll.closed = False
    session.commit()
    update_poll_messages(session, context.bot, poll)
