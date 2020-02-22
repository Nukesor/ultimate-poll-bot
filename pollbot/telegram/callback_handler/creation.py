"""Callback functions needed during creation of a Poll."""
from datetime import date
from pollbot.i18n import i18n
from pollbot.helper import poll_required
from pollbot.helper.creation import create_poll
from pollbot.helper.enums import PollType, ExpectedInput
from pollbot.telegram.keyboard import (
    get_change_poll_type_keyboard,
    get_init_keyboard,
    get_options_entered_keyboard,
    get_creation_datepicker_keyboard,
    get_open_datepicker_keyboard,
    get_init_settings_keyboard,
)
from pollbot.display.creation import (
    get_init_text,
    get_poll_type_help_text,
    get_datepicker_text,
    get_init_anonymziation_settings_text,
)

from pollbot.models import Poll
from .user import init_poll


async def open_init_text(event, poll):
    """Open the initial poll creation message."""
    keyboard = get_init_keyboard(poll)
    await event.edit(get_init_text(poll), buttons=keyboard)


async def open_anonymization_settings(event, poll):
    """Open the initial poll anonymization settings."""
    await event.edit(
        get_init_anonymziation_settings_text(poll),
        buttons=get_init_settings_keyboard(poll),
        link_preview=False,
    )


@poll_required
async def back_to_creation_init(session, context, event, poll):
    """Open the initial poll creation message."""
    await open_init_text(event, poll)


@poll_required
async def open_init_anonymization_settings(session, context, event, poll):
    """Open the anonymization settings for this poll."""
    await open_anonymization_settings(event, poll)


@poll_required
async def skip_description(session, context, event, poll):
    """Skip description creation step."""
    context.user.expected_input = ExpectedInput.options.name
    session.commit()
    await event.edit(
        i18n.t('creation.option.first', locale=context.user.locale),
        buttons=get_open_datepicker_keyboard(poll)
    )


@poll_required
async def show_poll_type_keyboard(session, context, event, poll):
    """Show to vote type keyboard."""
    poll = session.query(Poll).get(context.payload)

    keyboard = get_change_poll_type_keyboard(poll)
    await event.edit(get_poll_type_help_text(poll), buttons=keyboard)


@poll_required
async def change_poll_type(session, context, event, poll):
    """Change the vote type."""
    if poll.created:
        return i18n.t('callback.poll_created', locale=context.user.locale)

    poll.poll_type = PollType(context.action).name

    await open_init_text(event, poll)


@poll_required
async def toggle_anonymity(session, context, event, poll):
    """Change the anonymity settings of a poll."""
    if poll.created:
        return i18n.t('callback.poll_already_created', locale=context.user.locale)

    poll.anonymous = not poll.anonymous

    await open_anonymization_settings(event, poll)
    return i18n.t('callback.anonymity_changed', locale=context.user.locale)


@poll_required
async def toggle_results_visible(session, context, event, poll):
    """Change the results visible settings of a poll."""
    if poll.created:
        return i18n.t('callback.poll_already_created', locale=context.user.locale)

    poll.results_visible = not poll.results_visible

    await open_anonymization_settings(event, poll)
    return i18n.t('callback.visibility_changed', locale=context.user.locale)


@poll_required
async def all_options_entered(session, context, event, poll):
    """All options are entered the poll is created."""
    if poll is None:
        return

    locale = context.user.locale
    if poll.poll_type in [PollType.limited_vote.name, PollType.cumulative_vote.name]:
        await event.edit(i18n.t('creation.option.finished', locale=locale))
        context.user.expected_input = ExpectedInput.vote_count.name
        await event.respond(i18n.t('creation.vote_count_request', locale=locale))

        return

    await create_poll(session, poll, context.user, event, event)


@poll_required
async def open_creation_datepicker(session, context, event, poll):
    """All options are entered the poll is created."""
    keyboard = get_creation_datepicker_keyboard(poll, date.today())
    # Switch from new option by text to new option via datepicker
    if context.user.expected_input != ExpectedInput.options.name:
        await event.edit(i18n.t('creation.option.finished', locale=context.user.locale))
        return

    context.user.expected_input = ExpectedInput.date.name

    await event.edit(get_datepicker_text(poll), buttons=keyboard)


@poll_required
async def close_creation_datepicker(session, context, event, poll):
    """All options are entered the poll is created."""
    user = context.user
    if len(poll.options) == 0:
        text = i18n.t('creation.option.first', locale=user.locale)
        keyboard = get_open_datepicker_keyboard(poll)
    else:
        text = i18n.t('creation.option.next', locale=user.locale)
        keyboard = get_options_entered_keyboard(poll)

    # Replace the message completely, since all options have already been entered
    if user.expected_input != ExpectedInput.date.name:
        await event.edit(i18n.t('creation.option.finished', locale=user.locale))
        return

    user.expected_input = ExpectedInput.options.name
    await event.edit(text, buttons=keyboard)


async def cancel_creation(session, context, event):
    """Cancel the creation of a bot."""
    if context.poll is None:
        return i18n.t('delete.doesnt_exist', locale=context.user.locale)

    session.delete(context.poll)
    session.commit()
    await event.edit(
        i18n.t('delete.previous_deleted', locale=context.user.locale)
    )

    await init_poll(session, context, event)
