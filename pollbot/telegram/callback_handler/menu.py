"""Callback functions needed during creation of a Poll."""
from pollbot.helper.enums import CallbackResult, ExpectedInput

from pollbot.models import Reference
from pollbot.helper import poll_required
from pollbot.helper.display import get_poll_management_text, get_settings_text
from pollbot.telegram.keyboard import (
    get_change_vote_type_keyboard,
    get_deletion_confirmation,
    get_close_confirmation,
    get_management_keyboard,
    get_vote_keyboard,
    get_settings_keyboard,
)


@poll_required
def show_vote_type_keyboard(session, context, poll):
    """Change the initial keyboard to vote type keyboard."""
    keyboard = get_change_vote_type_keyboard(poll)
    context.query.message.edit_text(
        reply_markup=keyboard
    )


@poll_required
def go_back(session, context, poll):
    """Go back to the original step."""
    if context.callback_result == CallbackResult.main_menu:
        text = get_poll_management_text(session, poll, show_warning=False)
        keyboard = get_management_keyboard(poll)
        poll.in_settings = False

    elif context.callback_result == CallbackResult.settings:
        text = get_settings_text(poll)
        keyboard = get_settings_keyboard(poll)

    context.query.message.edit_text(
        text,
        parse_mode='markdown',
        reply_markup=keyboard,
    )

    # Reset the expected input from the previous option
    poll.expected_input = None


@poll_required
def show_vote_menu(session, context, poll):
    """Show the vote keyboard in the management interface."""
    keyboard = get_vote_keyboard(poll, show_back=True)
    # Set the expected_input to votes, since the user might want to vote multiple times
    poll.expected_input = ExpectedInput.votes.name
    context.query.message.edit_text(
        get_poll_management_text(session, poll),
        parse_mode='markdown',
        reply_markup=keyboard
    )


@poll_required
def show_settings(session, context, poll):
    """Show the settings tab."""
    text = get_settings_text(poll)
    keyboard = get_settings_keyboard(poll)
    context.query.message.edit_text(text, parse_mode='markdown', reply_markup=keyboard)
    poll.in_settings = True


@poll_required
def show_deletion_confirmation(session, context, poll):
    """Show the delete confirmation message."""
    context.query.message.edit_text(
        'Do you really want to delete this poll?',
        reply_markup=get_deletion_confirmation(poll),
    )


@poll_required
def show_close_confirmation(session, context, poll):
    """Show the delete confirmation message."""
    message = 'Do you really want to close this poll?\n'
    message += 'The results will become visible, but people will on longer be able to vote'
    context.query.message.edit_text(
        message,
        reply_markup=get_close_confirmation(poll),
    )


@poll_required
def show_menu(session, context, poll):
    """Replace the current message with the main poll menu."""
    message = context.query.message
    message.edit_text(
        get_poll_management_text(session, poll),
        parse_mode='markdown',
        reply_markup=get_management_keyboard(poll),
    )

    reference = Reference(
        poll,
        admin_chat_id=message.chat.id,
        admin_message_id=message.message_id
    )
    session.add(reference)
    session.commit()
