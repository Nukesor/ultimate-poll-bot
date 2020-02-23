"""Handle messages."""
from telethon import events

from pollbot.i18n import i18n
from pollbot.client import client
from pollbot.helper.session import message_wrapper
from pollbot.helper.enums import ExpectedInput, PollType
from pollbot.display import get_settings_text
from pollbot.helper.update import update_poll_messages
from pollbot.helper.creation import create_poll

from pollbot.helper.creation import (
    next_option,
    add_options,
)
from pollbot.telegram.keyboard import (
    get_settings_keyboard,
    get_open_datepicker_keyboard,
    get_skip_description_keyboard,
)

from pollbot.models import Reference


@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
@message_wrapper(private=True)
async def handle_private_text(event, session, user):
    """Read all private messages and the creation of polls."""
    text = event.text.strip()
    poll = user.current_poll

    if user.expected_input is None:
        return

    expected_input = ExpectedInput[user.expected_input]
    ignored_expected_inputs = [
        ExpectedInput.date,
        ExpectedInput.due_date,
        ExpectedInput.votes,
    ]
    # The user is currently not expecting input or no poll is set
    if user.current_poll is None or user.expected_input is None:
        return
    elif expected_input in ignored_expected_inputs:
        return
    else:
        actions = {
            ExpectedInput.name: handle_set_name,
            ExpectedInput.description: handle_set_description,
            ExpectedInput.options: handle_create_options,
            ExpectedInput.vote_count: handle_set_vote_count,
            ExpectedInput.new_option: handle_new_option,
            ExpectedInput.new_user_option: handle_user_option_addition,
        }
        if '*' in text or '_' in text or '[' in text or '`' in text:
            await event.respond(i18n.t('creation.error.markdown', locale=user.locale))
            return

        return await actions[expected_input](event, session, user, text, poll)


async def handle_set_name(event, session, user, text, poll):
    """Set the name of the poll."""
    poll.name = text
    user.expected_input = ExpectedInput.description.name
    keyboard = get_skip_description_keyboard(poll)
    await event.respond(
        i18n.t('creation.description', locale=user.locale),
        buttons=keyboard,
    )


async def handle_set_description(event, session, user, text, poll):
    """Set the description of the poll."""
    poll.description = text
    user.expected_input = ExpectedInput.options.name
    await event.respond(
        i18n.t('creation.option.first', locale=user.locale),
        buttons=get_open_datepicker_keyboard(poll),
    )


async def handle_create_options(event, session, user, text, poll):
    """Add options to the poll."""
    # Multiple options can be sent at once separated by newline
    # Strip them and ignore empty lines
    added_options = add_options(poll, text)

    if len(added_options) == 0:
        return i18n.t('creation.option.no_new', locale=user.locale)

    await next_option(event, poll, added_options)


async def handle_set_vote_count(event, session, user, text, poll):
    """Set the amount of possible votes for this poll."""
    if poll.poll_type == PollType.limited_vote.name:
        error_message = i18n.t('creation.error.limit_between', locale=user.locale, limit=len(poll.options))
    elif poll.poll_type == PollType.cumulative_vote.name:
        error_message = i18n.t('creation.error.limit_bigger_zero', locale=user.locale)

    try:
        amount = int(text)
    except BaseException:
        return error_message

    # Check for valid count
    if amount < 1 or (poll.poll_type == PollType.limited_vote.name and amount > len(poll.options)):
        return error_message

    if amount > 2000000000:
        return i18n.t('creation.error.too_big', locale=user.locale)

    poll.number_of_votes = amount

    await create_poll(session, poll, user, event)


async def handle_new_option(event, session, user, text, poll):
    """Add a new option after poll creation."""
    added_options = add_options(poll, text)

    if len(added_options) > 0:
        text = i18n.t('creation.option.multiple_added', locale=user.locale) + '\n'
        for option in added_options:
            text += f'\n*{option}*'
        await event.respond(text)
        poll.init_votes_for_new_options(session)
    else:
        await event.respond(i18n.t('creation.option.no_new', locale=user.locale))

    # Reset expected input
    user.current_poll = None
    user.expected_input = None

    text = get_settings_text(poll)
    keyboard = get_settings_keyboard(poll)
    message = await event.respond(text, buttons=keyboard)

    # Delete old references
    references = session.query(Reference) \
        .filter(Reference.poll == poll) \
        .filter(Reference.admin_user_id == event.from_id) \
        .all()
    for reference in references:
        try:
            await client.delete_messages(event.from_id, reference.admin_message_id)
        except:
            pass
        session.delete(reference)

    # Create new reference
    reference = Reference(
        poll,
        admin_user=user,
        admin_message_id=message.id
    )
    session.add(reference)
    session.commit()

    await update_poll_messages(session, poll)


async def handle_user_option_addition(event, session, user, text, poll):
    """Handle the addition of options from and arbitrary user."""
    if not poll.allow_new_options:
        user.current_poll = None
        user.expected_input = None
        await event.respond(i18n.t('creation.not_allowed', locale=user.locale))

    added_options = add_options(poll, text)

    if len(added_options) > 0:
        # Reset user
        user.current_poll = None
        user.expected_input = None

        # Send message
        text = i18n.t('creation.option.multiple_added', locale=user.locale) + '\n'
        for option in added_options:
            text += f'\n**{option}**'
        await event.respond(text)

        # Update all polls
        poll.init_votes_for_new_options(session)
        session.commit()
        await update_poll_messages(session, poll)
    else:
        await event.respond(i18n.t('creation.option.no_new', locale=user.locale))
