"""Callback functions needed during creation of a Poll."""
from pollbot.i18n import i18n
from pollbot.models import Reference
from pollbot.helper import poll_required
from pollbot.helper.enums import CallbackResult, ExpectedInput
from pollbot.display import (
    get_poll_text_and_vote_keyboard,
    get_settings_text,
    get_poll_text,
)
from pollbot.telegram.keyboard import (
    get_change_poll_type_keyboard,
    get_deletion_confirmation,
    get_close_confirmation,
    get_management_keyboard,
    get_settings_keyboard,
)


@poll_required
def show_poll_type_keyboard(session, context, poll):
    """Change the initial keyboard to vote type keyboard."""
    keyboard = get_change_poll_type_keyboard(poll)
    context.query.message.edit_text(
        reply_markup=keyboard
    )


@poll_required
def go_back(session, context, poll):
    """Go back to the original step."""
    if context.callback_result == CallbackResult.main_menu:
        text = get_poll_text(session, poll)
        keyboard = get_management_keyboard(poll)
        poll.in_settings = False

    elif context.callback_result == CallbackResult.settings:
        text = get_settings_text(poll)
        keyboard = get_settings_keyboard(poll)

    context.query.message.edit_text(
        text,
        parse_mode='markdown',
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )

    # Reset the expected input from the previous option
    context.user.expected_input = None


@poll_required
def show_vote_menu(session, context, poll):
    """Show the vote keyboard in the management interface."""
    text, keyboard = get_poll_text_and_vote_keyboard(session, poll, user=context.user, show_back=True)
    # Set the expected_input to votes, since the user might want to vote multiple times
    context.user.expected_input = ExpectedInput.votes.name
    context.query.message.edit_text(
        text,
        parse_mode='markdown',
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


@poll_required
def show_settings(session, context, poll):
    """Show the settings tab."""
    text = get_settings_text(poll)
    keyboard = get_settings_keyboard(poll)
    context.query.message.edit_text(
        text,
        parse_mode='markdown',
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )
    poll.in_settings = True


@poll_required
def show_deletion_confirmation(session, context, poll):
    """Show the delete confirmation message."""
    context.query.message.edit_text(
        i18n.t('management.delete', locale=poll.user.locale),
        reply_markup=get_deletion_confirmation(poll),
    )


@poll_required
def show_close_confirmation(session, context, poll):
    """Show the permanent close confirmation message."""
    context.query.message.edit_text(
        i18n.t('management.permanently_close', locale=poll.user.locale),
        reply_markup=get_close_confirmation(poll),
    )


@poll_required
def show_menu(session, context, poll):
    """Replace the current message with the main poll menu."""
    message = context.query.message
    message.edit_text(
        get_poll_text(session, poll),
        parse_mode='markdown',
        reply_markup=get_management_keyboard(poll),
        disable_web_page_preview=True,
    )

    reference = Reference(
        poll,
        admin_user=context.user,
        admin_message_id=message.message_id
    )
    session.add(reference)
    session.commit()
