"""Callback functions needed during creation of a Poll."""
from pollbot.i18n import i18n
from pollbot.models import Reference
from pollbot.helper import poll_required
from pollbot.helper.enums import CallbackResult, ExpectedInput
from pollbot.display import get_settings_text
from pollbot.display.poll.compilation import (
    get_poll_text_and_vote_keyboard,
    get_poll_text
)
from pollbot.telegram.keyboard import (
    get_change_poll_type_keyboard,
    get_deletion_confirmation,
    get_close_confirmation,
    get_management_keyboard,
    get_settings_keyboard,
)


@poll_required
async def show_poll_type_keyboard(session, context, event, poll):
    """Change the initial keyboard to vote type keyboard."""
    keyboard = get_change_poll_type_keyboard(poll)
    await event.edit(
        buttons=keyboard
    )


@poll_required
async def go_back(session, context, event, poll):
    """Go back to the original step."""
    if context.callback_result == CallbackResult.main_menu:
        text = get_poll_text(session, poll)
        keyboard = get_management_keyboard(poll)
        poll.in_settings = False

    elif context.callback_result == CallbackResult.settings:
        text = get_settings_text(poll)
        keyboard = get_settings_keyboard(poll)

    await event.edit(text, buttons=keyboard, link_preview=False)

    # Reset the expected input from the previous option
    context.user.expected_input = None


@poll_required
async def show_vote_menu(session, context, event, poll):
    """Show the vote keyboard in the management interface."""
    if poll.is_priority():
        poll.init_votes(session, context, event.user)
        session.commit()

    text, keyboard = get_poll_text_and_vote_keyboard(
        session,
        poll,
        user=context.user,
        show_back=True,
    )
    # Set the expected_input to votes, since the user might want to vote multiple times
    context.user.expected_input = ExpectedInput.votes.name
    await event.edit(text, buttons=keyboard, link_preview=False)


@poll_required
async def show_settings(session, context, event, poll):
    """Show the settings tab."""
    text = get_settings_text(poll)
    keyboard = get_settings_keyboard(poll)
    await event.edit(
        text,
        buttons=keyboard,
        link_preview=False,
    )
    poll.in_settings = True


@poll_required
async def show_deletion_confirmation(session, context, event, poll):
    """Show the delete confirmation message."""
    await event.edit(
        i18n.t('management.delete', locale=poll.user.locale),
        buttons=get_deletion_confirmation(poll),
    )


@poll_required
async def show_close_confirmation(session, context, event, poll):
    """Show the permanent close confirmation message."""
    await event.edit(
        i18n.t('management.permanently_close', locale=poll.user.locale),
        buttons=get_close_confirmation(poll),
    )


@poll_required
async def show_menu(session, context, event, poll):
    """Replace the current message with the main poll menu."""
    await event.edit(
        get_poll_text(session, poll),
        buttons=get_management_keyboard(poll),
        link_preview=False,
    )

    reference = Reference(
        poll,
        admin_user=context.user,
        admin_message_id=event.message_id,
    )
    session.add(reference)
    session.commit()
