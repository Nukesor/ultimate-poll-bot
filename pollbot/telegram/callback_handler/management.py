"""Callback functions needed during creation of a Poll."""
from datetime import datetime
from pollbot.helper import poll_required
from pollbot.helper.update import remove_poll_messages, update_poll_messages
from pollbot.helper.display import get_poll_management_text
from pollbot.telegram.keyboard import get_management_keyboard


@poll_required
def delete_poll(session, context, poll):
    """Permanently delete the pall."""
    remove_poll_messages(session, context.bot, poll)
    session.delete(poll)
    session.commit()
    context.query.answer('Poll deleted.')


@poll_required
def close_poll(session, context, poll):
    """Close this poll."""
    poll.closed = True
    session.commit()
    update_poll_messages(session, context.bot, poll)
    context.query.answer('Poll closed.')


@poll_required
def reopen_poll(session, context, poll):
    """Reopen this poll."""
    if not poll.results_visible:
        context.query.answer('Poll cannot be reopened')
        return
    poll.closed = False
    if poll.due_date is not None and poll.due_date <= datetime.now():
        poll.due_date = None
        poll.next_notification = None
    session.commit()
    update_poll_messages(session, context.bot, poll)


@poll_required
def reset_poll(session, context, poll):
    """Reset this poll."""
    for vote in poll.votes:
        session.delete(vote)
    session.commit()
    update_poll_messages(session, context.bot, poll)
    context.query.answer('All votes have been removed')


@poll_required
def clone_poll(session, context, poll):
    """Clone this poll."""
    new_poll = poll.clone(session)
    session.commit()

    context.tg_chat.send_message(
            get_poll_management_text(session, new_poll),
            parse_mode='markdown',
            reply_markup=get_management_keyboard(new_poll)
        )
    context.query.answer('Poll cloned.')
