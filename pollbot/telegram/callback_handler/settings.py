"""Callback functions needed during creation of a Poll."""
from datetime import date
from pollbot.i18n import i18n
from pollbot.helper import poll_required
from pollbot.helper.update import update_poll_messages
from pollbot.display import get_settings_text
from pollbot.display.poll.compilation import get_poll_text
from pollbot.display.creation import get_datepicker_text
from pollbot.telegram.keyboard import (
    get_anonymization_confirmation_keyboard,
    get_settings_keyboard,
    get_styling_settings_keyboard,
    get_remove_option_keyboard,
    get_add_option_keyboard,
    get_add_option_datepicker_keyboard,
    get_due_date_datepicker_keyboard,
    get_settings_language_keyboard,
)
from pollbot.helper.enums import ExpectedInput, DatepickerContext
from pollbot.models import PollOption, User, Vote


async def send_settings_message(context):
    """Edit the message of the current context to the settings menu."""
    await context.event.edit(
        get_settings_text(context.poll),
        buttons=get_settings_keyboard(context.poll),
        link_preview=False,
    )


@poll_required
async def show_anonymization_confirmation(session, context, event, poll):
    """Show the delete confirmation message."""
    await event.edit(
        i18n.t('settings.anonymize', locale=poll.user.locale),
        buttons=get_anonymization_confirmation_keyboard(poll),
    )


@poll_required
async def make_anonymous(session, context, event, poll):
    """Change the anonymity settings of a poll."""
    poll.anonymous = True
    if not poll.show_percentage and not poll.show_option_votes:
        poll.show_percentage = True

    session.commit()
    await update_poll_messages(session, poll)
    await send_settings_message(context)


@poll_required
async def open_language_picker(session, context, event, poll):
    """Open the language picker."""
    keyboard = get_settings_language_keyboard(poll)
    await event.edit(
        i18n.t('settings.change_language', locale=poll.user.locale),
        buttons=keyboard,
    )


@poll_required
async def change_poll_language(session, context, event, poll):
    """Open the language picker."""
    poll.locale = context.action
    session.commit()
    await send_settings_message(context)


@poll_required
async def open_due_date_datepicker(session, context, event, poll):
    """Open the datepicker for setting a due date."""
    poll.user.expected_input = ExpectedInput.due_date.name
    keyboard = get_due_date_datepicker_keyboard(poll, date.today())
    context.query.message.edit_buttons(
        buttons=keyboard
    )


@poll_required
async def show_styling_menu(session, context, event, poll):
    """Show the menu for sorting settings."""
    await event.edit(
        get_poll_text(session, context, event.poll),
        buttons=get_styling_settings_keyboard(poll),
        link_preview=False,
    )


@poll_required
async def expect_new_option(session, context, event, poll):
    """Send a text and tell the user that we expect a new option."""
    user = context.user
    user.expected_input = ExpectedInput.new_option.name
    user.current_poll = poll

    await event.edit(
        text=i18n.t('creation.option.first', locale=user.locale),
        buttons=get_add_option_keyboard(poll),
    )


@poll_required
async def open_new_option_datepicker(session, context, event, poll):
    """Send a text and tell the user that we expect a new option."""
    keyboard = get_add_option_datepicker_keyboard(poll, date.today())
    await event.edit(
        text=get_datepicker_text(poll),
        buttons=keyboard,
    )


@poll_required
async def show_remove_options_menu(session, context, event, poll):
    """Show the menu for removing options."""
    keyboard = get_remove_option_keyboard(poll)
    await event.edit(
        i18n.t('settings.remove_options', locale=poll.user.locale),
        buttons=keyboard,
    )


@poll_required
async def remove_option(session, context, event, poll):
    """Remove the option."""
    session.query(PollOption) \
        .filter(PollOption.id == context.action) \
        .delete()

    if poll.is_priority():
        users = session.query(User) \
            .join(User.votes) \
            .filter(Vote.poll == poll) \
            .all()

        for user in users:
            votes = session.query(Vote) \
                .filter(Vote.poll == poll) \
                .filter(Vote.user == user) \
                .order_by(Vote.priority.asc()) \
                .all()

            for index, vote in enumerate(votes):
                vote.priority = index
                session.commit()

    session.commit()

    keyboard = get_remove_option_keyboard(poll)
    context.query.message.edit_buttons(buttons=keyboard)

    await update_poll_messages(session, poll)


@poll_required
async def toggle_allow_new_options(session, context, event, poll):
    """Toggle the visibility of the percentage bar."""
    poll.allow_new_options = not poll.allow_new_options

    session.commit()
    await update_poll_messages(session, poll)
    await send_settings_message(context)
