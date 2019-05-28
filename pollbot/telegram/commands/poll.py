"""Poll related commands."""
from telegram.ext import run_async

from pollbot.helper.session import session_wrapper
from pollbot.helper.enums import PollCreationStep
from pollbot.helper.creation import get_init_text
from pollbot.helper.keyboard import get_main_keyboard, get_init_keyboard

from pollbot.models import Poll


@run_async
@session_wrapper(private=True)
def create_poll(bot, update, session, user):
    """Create a new poll."""
    # The previous unfinished poll will be removed
    if user.current_poll is not None \
       and user.current_poll.creation_step != PollCreationStep.done.name:
        session.delete(user.current_poll)

    poll = Poll(user)
    user.current_poll = poll
    session.add(poll)
    session.commit()

    text = get_init_text(poll)
    keyboard = get_init_keyboard(poll)

    update.message.chat.send_message(text, reply_markup=keyboard)


@run_async
@session_wrapper(private=True)
def cancel_creation(bot, update, session, user):
    """Create a new poll."""
    # The previous unfinished poll will be removed
    if user.current_poll is not None \
       and user.current_poll.creation_step != PollCreationStep.done.name:
        session.delete(user.current_poll)
        session.commit()

    keyboard = get_main_keyboard()
    update.message.chat.send_message('Poll creation canceled', reply_markup=keyboard)
