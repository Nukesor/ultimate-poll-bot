"""Admin related stuff."""
import time
from telegram.ext import run_async
from telegram.error import BadRequest, Unauthorized

from pollbot.helper.session import session_wrapper
from pollbot.models import User, Poll
from pollbot.config import config


@run_async
@session_wrapper()
def broadcast(bot, update, session, user):
    """Broadcast a message to all users."""
    if user.username.lower() != config['telegram']['admin'].lower():
        return 'You are not allowed to do this'
    message = update.message.text.split(' ', 1)[1].strip()

    users = session.query(User).all()

    update.message.chat.send_message(f'Sending broadcast to {len(users)} chats.')
    for user in users:
        try:
            bot.send_message(user.id, message, parse_mode='Markdown')

        # The chat doesn't exist any longer, delete it
        except BadRequest as e:
            if e.message == 'Chat not found': # noqa
                pass

        # We are not allowed to contact this user.
        except Unauthorized:
            pass

        # Sleep one second to not trigger flood prevention
        time.sleep(1)

    update.message.chat.send_message('All messages sent')


@run_async
@session_wrapper()
def test_broadcast(bot, update, session, user):
    """Send the broadcast message to the admin for test purposes."""
    if user.username.lower() != config['telegram']['admin'].lower():
        return 'You are not allowed to do this'
    message = update.message.text.split(' ', 1)[1].strip()

    bot.send_message(user.id, message, parse_mode='Markdown')


@run_async
@session_wrapper()
def stats(bot, update, session, user):
    """Send the broadcast message to the admin for test purposes."""
    if user.username.lower() != config['telegram']['admin'].lower():
        return 'You are not allowed to do this'

    # User stats
    total_users = session.query(User.id).count()
    users_owning_polls = session.query(User) \
        .join(User.polls) \
        .group_by(User) \
        .count()
    users_with_votes = session.query(User) \
        .join(User.votes) \
        .group_by(User) \
        .count()

    # Polls
    highest_id = session.query(Poll.id).order_by(Poll.id.desc()).first()[0]
    total_polls = session.query(Poll).count()
    open_polls = session.query(Poll) \
        .filter(Poll.closed.is_(False)) \
        .count()
    closed_polls = session.query(Poll) \
        .filter(Poll.closed.is_(True)) \
        .count()

    # Poll types
    single = session.query(Poll).filter(Poll.poll_type == 'single_vote').count()
    doodle = session.query(Poll).filter(Poll.poll_type == 'doodle').count()
    block = session.query(Poll).filter(Poll.poll_type == 'block_vote').count()
    limited = session.query(Poll).filter(Poll.poll_type == 'limited_vote').count()
    cumulative = session.query(Poll).filter(Poll.poll_type == 'cumulative_vote').count()
    count = session.query(Poll).filter(Poll.poll_type == 'count_vote').count()

    single_percent = single/total_polls * 100
    doodle_percent = doodle/total_polls * 100
    block_percent = block/total_polls * 100
    limited_percent = limited/total_polls * 100
    cumulative_percent = cumulative/total_polls * 100
    count_percent = count/total_polls * 100

    message = f"""Stats:

Users:
    Total: {total_users}
    Owning polls: {users_owning_polls}
    Voted: {users_with_votes}

Polls:
    Highest ID: {highest_id}
    Total: {total_polls}
    Open: {open_polls}
    Closed: {closed_polls}
    Deleted: {highest_id - total_polls}

Types:
    Single:  {single} ({single_percent:.2f}%)
    Doodle: {doodle} ({doodle_percent:.2f}%)
    Block: {block} ({block_percent:.2f}%)
    Limited: {limited} ({limited_percent:.2f}%)
    Cumulative: {cumulative} ({cumulative_percent:.2f}%)
    Count: {count} ({count_percent:.2f}%)
"""

    bot.send_message(user.id, message)
