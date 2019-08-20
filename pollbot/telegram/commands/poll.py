"""Poll related commands."""
from telegram.ext import run_async

from pollbot.i18n import i18n
from pollbot.helper.session import session_wrapper
from pollbot.display.creation import get_init_text
from pollbot.helper.enums import ExpectedInput
from pollbot.telegram.keyboard import (
    get_cancel_creation_keyboard,
    get_init_keyboard,
    get_poll_list_keyboard,
)

from pollbot.models import Poll


@run_async
@session_wrapper(private=True)
def create_poll(bot, update, session, user):
    """Create a new poll."""
    # The previous unfinished poll will be removed
    user.started = True
    if user.current_poll is not None and not user.current_poll.created:
        update.message.chat.send_message(
            i18n.t('creation.already_creating', locale=user.locale),
            reply_markup=get_cancel_creation_keyboard(user.current_poll))
        return

    poll = Poll(user)
    poll.european_date_format = user.european_date_format
    poll.locale = user.locale
    user.current_poll = poll
    user.expected_input = ExpectedInput.name.name
    session.add(poll)
    session.commit()

    text = get_init_text(poll)
    keyboard = get_init_keyboard(poll)

    update.message.chat.send_message(text, parse_mode='markdown', reply_markup=keyboard)


@run_async
@session_wrapper(private=True)
def list_polls(bot, update, session, user):
    """Get a list of all active polls."""
    text = i18n.t('list.polls', locale=user.locale)
    polls = session.query(Poll) \
        .filter(Poll.user == user) \
        .filter(Poll.created.is_(True)) \
        .filter(Poll.closed.is_(False)) \
        .all()

    if len(polls) == 0:
        return i18n.t('list.no_polls', locale=user.locale)

    keyboard = get_poll_list_keyboard(polls)
    update.message.chat.send_message(text, reply_markup=keyboard)


@run_async
@session_wrapper(private=True)
def list_closed_polls(bot, update, session, user):
    """Get a list of all active polls."""
    text = i18n.t('list.polls', locale=user.locale)
    polls = session.query(Poll) \
        .filter(Poll.user == user) \
        .filter(Poll.created.is_(True)) \
        .filter(Poll.closed.is_(True)) \
        .all()

    if len(polls) == 0:
        return i18n.t('list.no_closed_polls', locale=user.locale)

    keyboard = get_poll_list_keyboard(polls)
    update.message.chat.send_message(text, reply_markup=keyboard)


@run_async
@session_wrapper(private=True)
def delete_all(bot, update, session, user):
    """Delete all polls of the user."""
    for poll in user.polls:
        session.delete(poll)

    return i18n.t('deleted.polls', locale=user.locale)


@run_async
@session_wrapper(private=True)
def delete_all_closed(bot, update, session, user):
    """Delete all closed polls of the user."""
    for poll in user.polls:
        if poll.closed:
            session.delete(poll)

    return i18n.t('deleted.closed_polls', locale=user.locale)
