"""Callback functions needed during creation of a Poll."""
from pollbot.helper.enums import CallbackResult, ExpectedInput

from pollbot.helper.display import get_poll_management_text, get_options_text
from pollbot.telegram.keyboard import (
    get_change_vote_type_keyboard,
    get_deletion_confirmation,
    get_management_keyboard,
    get_vote_keyboard,
    get_options_keyboard,
)


def show_vote_type_keyboard(session, context):
    """Change the initial keyboard to vote type keyboard."""
    keyboard = get_change_vote_type_keyboard(context.poll)
    context.query.message.edit_text(
        reply_markup=keyboard
    )


def go_back(session, context):
    """Go back to the original step."""
    if context.callback_result == CallbackResult.main_menu:
        text = get_poll_management_text(session, context.poll)
        keyboard = get_management_keyboard(context.poll)

    elif context.callback_result == CallbackResult.options:
        text = get_options_text(context.poll),
        keyboard = get_options_keyboard(context.poll)

    context.query.message.edit_text(
        text,
        parse_mode='markdown',
        reply_markup=keyboard,
    )

    # Reset the expected input from the previous option
    context.poll.expected_input = None


def show_vote_menu(session, context):
    """Show the vote keyboard in the management interface."""
    keyboard = get_vote_keyboard(context.poll, show_back=True)
    # Set the expected_input to votes, since the user might want to vote multiple times
    context.poll.expected_input = ExpectedInput.votes.name

    context.query.message.edit_reply_markup(reply_markup=keyboard)


def show_options(session, context):
    """Show the options tab."""
    text = get_options_text(context.poll)
    keyboard = get_options_keyboard(context.poll)
    context.query.message.edit_text(text, parse_mode='markdown', reply_markup=keyboard)


def show_deletion_confirmation(session, context):
    """Show the delete confirmation message."""
    context.query.message.edit_text(
        'Do you really want to delete this poll?',
        reply_markup=get_deletion_confirmation(context.poll),
    )


def show_menu(session, context):
    """Replace the current message with the main poll menu."""
    context.query.message.edit_text(
        get_poll_management_text(session, context.poll),
        parse_mode='markdown',
        reply_markup=get_management_keyboard(context.poll),
    )
