"""Handle messages."""
from typing import Optional

from sqlalchemy.orm.scoping import scoped_session
from telegram.bot import Bot
from telegram.chat import Chat
from telegram.update import Update

from pollbot.display import get_settings_text
from pollbot.display.poll.option import next_option
from pollbot.enums import ExpectedInput, PollType, ReferenceType
from pollbot.helper import markdown_characters
from pollbot.i18n import i18n
from pollbot.models import Reference
from pollbot.models.poll import Poll
from pollbot.models.user import User
from pollbot.poll.helper import remove_old_references
from pollbot.poll.option import add_options_multiline
from pollbot.poll.update import update_poll_messages
from pollbot.telegram.callback_handler.creation import create_poll
from pollbot.telegram.keyboard.creation import (
    get_open_datepicker_keyboard,
    get_skip_description_keyboard,
)
from pollbot.telegram.keyboard.settings import get_settings_keyboard
from pollbot.telegram.session import message_wrapper


@message_wrapper()
def handle_private_text(
    bot: Bot, update: Update, session: scoped_session, user: User
) -> Optional[str]:
    """Read all private messages and the creation of polls."""
    text = update.message.text.strip()
    poll = user.current_poll
    chat = update.message.chat

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
        for char in markdown_characters:
            if char in text:
                chat.send_message(
                    i18n.t("creation.error.markdown", locale=user.locale),
                    parse_mode="Markdown",
                )
                return

        return actions[expected_input](bot, update, session, user, text, poll, chat)


def handle_set_name(
    bot: Bot,
    update: Update,
    session: scoped_session,
    user: User,
    text: str,
    poll: Poll,
    chat: Chat,
) -> None:
    """Set the name of the poll."""
    poll.name = text

    if poll.name is None:
        return i18n.t("creation.error.invalid_poll_name", locale=user.locale)

    user.expected_input = ExpectedInput.description.name
    keyboard = get_skip_description_keyboard(poll)
    chat.send_message(
        i18n.t("creation.description", locale=user.locale),
        reply_markup=keyboard,
    )


def handle_set_description(
    bot: Bot,
    update: Update,
    session: scoped_session,
    user: User,
    text: str,
    poll: Poll,
    chat: Chat,
) -> None:
    """Set the description of the poll."""
    poll.description = text

    if len(poll.options) == 0:
        user.expected_input = ExpectedInput.options.name
        chat.send_message(
            i18n.t("creation.option.first", locale=user.locale),
            reply_markup=get_open_datepicker_keyboard(poll),
            parse_mode="markdown",
        )
    else:  # options were already prefilled e.g. by native poll
        create_poll(session, poll, user, update.effective_chat)


def handle_create_options(
    bot: Bot,
    update: Update,
    session: scoped_session,
    user: User,
    text: str,
    poll: Poll,
    chat: Chat,
) -> Optional[str]:
    """Add options to the poll."""
    # Multiple options can be sent at once separated by newline
    # Strip them and ignore empty lines
    added_options = add_options_multiline(session, poll, text)

    if len(added_options) == 0:
        return i18n.t("creation.option.no_new", locale=user.locale)

    next_option(chat, poll, added_options)


def handle_set_vote_count(
    bot: Bot,
    update: Update,
    session: scoped_session,
    user: User,
    text: str,
    poll: Poll,
    chat: Chat,
) -> Optional[str]:
    """Set the amount of possible votes for this poll."""
    if poll.poll_type == PollType.limited_vote.name:
        error_message = i18n.t(
            "creation.error.limit_between", locale=user.locale, limit=len(poll.options)
        )
    elif poll.poll_type == PollType.cumulative_vote.name:
        error_message = i18n.t("creation.error.limit_bigger_zero", locale=user.locale)

    try:
        amount = int(text)
    except BaseException:
        return error_message

    # Check for valid count
    if amount < 1 or (
        poll.poll_type == PollType.limited_vote.name and amount > len(poll.options)
    ):
        return error_message

    if amount > 2000000000:
        return i18n.t("creation.error.too_big", locale=user.locale)

    poll.number_of_votes = amount

    create_poll(session, poll, user, chat)


def handle_new_option(
    bot: Bot,
    update: Update,
    session: scoped_session,
    user: User,
    text: str,
    poll: Poll,
    chat: Chat,
) -> None:
    """Add a new option after poll creation."""
    added_options = add_options_multiline(session, poll, text)

    if len(added_options) > 0:
        text = i18n.t("creation.option.multiple_added", locale=user.locale) + "\n"
        for option in added_options:
            text += f"\n*{option}*"
        chat.send_message(text, parse_mode="markdown")
    else:
        chat.send_message(i18n.t("creation.option.no_new", locale=user.locale))

    # Reset expected input
    user.current_poll = None
    user.expected_input = None

    text = get_settings_text(poll)
    keyboard = get_settings_keyboard(poll)
    message = chat.send_message(
        text,
        parse_mode="markdown",
        reply_markup=keyboard,
    )

    remove_old_references(session, bot, poll, user)

    # Create new reference
    reference = Reference(
        poll, ReferenceType.admin.name, user=user, message_id=message.message_id
    )
    session.add(reference)
    session.commit()

    update_poll_messages(session, bot, poll, message.message_id, user)


def handle_user_option_addition(
    bot: Bot,
    update: Update,
    session: scoped_session,
    user: User,
    text: str,
    poll: Poll,
    chat: Chat,
) -> None:
    """Handle the addition of options from and arbitrary user."""
    if not poll.allow_new_options:
        user.current_poll = None
        user.expected_input = None
        chat.send_message(i18n.t("creation.not_allowed", locale=user.locale))

    added_options = add_options_multiline(session, poll, text)

    if len(added_options) > 0:
        # Reset user
        user.current_poll = None
        user.expected_input = None

        session.commit()

        # Send success message
        text = i18n.t("creation.option.multiple_added", locale=user.locale) + "\n"
        for option in added_options:
            text += f"\n*{option}*"
        chat.send_message(text, parse_mode="markdown")

        # Update all polls
        update_poll_messages(session, bot, poll)
    else:
        chat.send_message(i18n.t("creation.option.no_new", locale=user.locale))
