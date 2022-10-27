"""Callback functions needed during creation of a Poll."""

from sqlalchemy.orm.scoping import scoped_session

from pollbot.decorators import poll_required
from pollbot.display import get_settings_text
from pollbot.display.poll.compilation import (
    get_poll_text,
    get_poll_text_and_vote_keyboard,
)
from pollbot.enums import CallbackResult, ExpectedInput, ReferenceType
from pollbot.i18n import i18n
from pollbot.models import Reference
from pollbot.models.poll import Poll
from pollbot.poll.helper import remove_old_references
from pollbot.poll.vote import init_votes
from pollbot.telegram.callback_handler.context import CallbackContext
from pollbot.telegram.keyboard.management import (
    get_close_confirmation,
    get_deletion_confirmation,
    get_management_keyboard,
)
from pollbot.telegram.keyboard.settings import get_settings_keyboard


@poll_required
def go_back(session: scoped_session, context: CallbackContext, poll: Poll) -> None:

    """Go back to the original step."""
    if context.callback_result == CallbackResult.main_menu:
        text = get_poll_text(session, poll)
        keyboard = get_management_keyboard(poll)
        poll.in_settings = False

    elif context.callback_result == CallbackResult.settings:
        text = get_settings_text(poll)
        keyboard = get_settings_keyboard(poll)
    else:
        raise Exception(f"Got unknown callback result {context.callback_result}")

    context.query.message.edit_text(
        text,
        parse_mode="markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )

    # Reset the expected input from the previous option
    context.user.expected_input = None


@poll_required
def show_vote_menu(
    session: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """Show the vote keyboard in the management interface."""
    if poll.is_priority():
        init_votes(session, poll, context.user)
        session.commit()

    text, keyboard = get_poll_text_and_vote_keyboard(
        session, poll, user=context.user, show_back=True
    )
    # Set the expected_input to votes, since the user might want to vote multiple times
    context.user.expected_input = ExpectedInput.votes.name
    context.query.message.edit_text(
        text,
        parse_mode="markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


@poll_required
def show_settings(_: scoped_session, context: CallbackContext, poll: Poll) -> None:
    """Show the settings tab."""
    text = get_settings_text(poll)
    keyboard = get_settings_keyboard(poll)
    context.query.message.edit_text(
        text,
        parse_mode="markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )
    poll.in_settings = True


@poll_required
def show_deletion_confirmation(
    _: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """Show the delete confirmation message."""
    context.query.message.edit_text(
        i18n.t("management.delete", locale=poll.user.locale),
        reply_markup=get_deletion_confirmation(poll),
    )


@poll_required
def show_close_confirmation(
    _: scoped_session, context: CallbackContext, poll: Poll
) -> None:
    """Show the permanent close confirmation message."""
    context.query.message.edit_text(
        i18n.t("management.permanently_close", locale=poll.user.locale),
        reply_markup=get_close_confirmation(poll),
    )


@poll_required
def show_menu(session: scoped_session, context: CallbackContext, poll: Poll) -> None:
    """Replace the current message with the main poll menu."""
    message = context.query.message
    message.edit_text(
        get_poll_text(session, poll),
        parse_mode="markdown",
        reply_markup=get_management_keyboard(poll),
        disable_web_page_preview=True,
    )
    remove_old_references(session, context.bot, poll, context.user)

    reference = Reference(
        poll, ReferenceType.admin.name, user=context.user, message_id=message.message_id
    )
    session.add(reference)
    session.flush()
