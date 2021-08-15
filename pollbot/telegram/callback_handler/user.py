"""User related callback handler."""
from sqlalchemy.orm.scoping import scoped_session

from pollbot.display.misc import get_help_text_and_keyboard, get_poll_list
from pollbot.display.settings import get_user_settings_text
from pollbot.enums import PollDeletionMode
from pollbot.i18n import i18n
from pollbot.poll.creation import initialize_poll
from pollbot.poll.update import update_poll_messages
from pollbot.telegram.callback_handler.context import CallbackContext
from pollbot.telegram.keyboard.user import (
    get_delete_all_confirmation_keyboard,
    get_delete_user_final_confirmation_keyboard,
    get_main_keyboard,
    get_user_language_keyboard,
    get_user_settings_keyboard,
)


def open_main_menu(_: scoped_session, context: CallbackContext) -> None:
    """Open the main menu."""
    keyboard = get_main_keyboard(context.user)
    context.query.message.edit_text(
        i18n.t("misc.start", locale=context.user.locale),
        reply_markup=keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )


def open_user_settings(_: scoped_session, context: CallbackContext) -> None:
    """Open the user settings."""
    keyboard = get_user_settings_keyboard(context.user)
    text = get_user_settings_text(context.user)
    context.query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")


def open_language_menu(_: scoped_session, context: CallbackContext) -> None:
    """Open the user language selection menu."""
    keyboard = get_user_language_keyboard(context.user)
    context.query.message.edit_text(
        i18n.t("settings.change_language", locale=context.user.locale),
        parse_mode="markdown",
        reply_markup=keyboard,
    )


def list_polls(session: scoped_session, context: CallbackContext) -> None:
    """List all open polls of a user."""
    text, keyboard = get_poll_list(session, context.user, 0)
    context.query.message.chat.send_message(text, reply_markup=keyboard)


def list_closed_polls(session: scoped_session, context: CallbackContext) -> None:
    """List all open polls of a user."""
    text, keyboard = get_poll_list(session, context.user, 0, closed=True)
    context.query.message.chat.send_message(text, reply_markup=keyboard)


def list_polls_navigation(session: scoped_session, context: CallbackContext) -> None:
    """List all open polls of a user."""
    text, keyboard = get_poll_list(session, context.user, int(context.payload))
    context.query.message.edit_text(text, reply_markup=keyboard)


def list_closed_polls_navigation(
    session: scoped_session, context: CallbackContext
) -> None:
    """List all open polls of a user."""
    text, keyboard = get_poll_list(
        session, context.user, int(context.payload), closed=True
    )
    context.query.message.edit_text(text, reply_markup=keyboard)


def open_help(_: scoped_session, context: CallbackContext) -> None:
    """Open the help text."""
    text, keyboard = get_help_text_and_keyboard(context.user, "intro")
    context.query.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


def init_poll(session: scoped_session, context: CallbackContext) -> None:
    """Start the creation of a new poll."""
    user = context.user
    chat = context.query.message.chat

    initialize_poll(session, user, chat)


def toggle_notification(session: scoped_session, context: CallbackContext) -> None:
    """Toggle the notification settings of the user."""
    user = context.user
    user.notifications_enabled = not user.notifications_enabled
    session.commit()
    open_user_settings(session, context)


def change_user_language(session: scoped_session, context: CallbackContext) -> str:
    """Open the language picker."""
    context.user.locale = context.action
    session.commit()
    open_user_settings(session, context)
    return i18n.t("user.language_changed", locale=context.user.locale)


def delete_all_confirmation(_: scoped_session, context: CallbackContext) -> None:
    keyboard = get_delete_all_confirmation_keyboard(context.user)
    context.query.message.edit_text(
        i18n.t("settings.user.delete_all_confirmation", locale=context.user.locale),
        parse_mode="markdown",
        reply_markup=keyboard,
    )


def delete_closed_confirmation(_: scoped_session, context: CallbackContext) -> None:
    keyboard = get_delete_all_confirmation_keyboard(context.user, closed=True)
    context.query.message.edit_text(
        i18n.t("settings.user.delete_closed_confirmation", locale=context.user.locale),
        parse_mode="markdown",
        reply_markup=keyboard,
    )


def delete_all(session: scoped_session, context: CallbackContext) -> str:
    """Delete all polls of the user."""
    for poll in context.user.polls:
        if poll.delete is None:
            poll.delete = PollDeletionMode.DB_ONLY.name
    session.commit()

    open_user_settings(session, context)
    return i18n.t("deleted.polls", locale=context.user.locale)


def delete_closed(session: scoped_session, context: CallbackContext) -> str:
    """Delete all closed polls of the user."""
    for poll in context.user.polls:
        if poll.delete is None:
            poll.delete = PollDeletionMode.WITH_MESSAGES.name
    session.commit()

    open_user_settings(session, context)
    return i18n.t("deleted.closed_polls", locale=context.user.locale)


def delete_user_second_confirmation(
    _: scoped_session, context: CallbackContext
) -> None:
    """Delete everything of a user and ban them forever."""
    user = context.user
    context.query.message.edit_text(
        i18n.t("misc.final_deletion_warning", locale=user.locale),
        reply_markup=get_delete_user_final_confirmation_keyboard(user),
        parse_mode="markdown",
    )


def delete_user(session: scoped_session, context: CallbackContext) -> None:
    """Delete everything of a user and ban them forever."""
    user = context.user

    for poll in context.user.polls:
        if poll.delete is None:
            poll.delete = PollDeletionMode.DB_ONLY.name
    session.commit()

    polls_for_update = []
    # Delete all votes, but only update non-closed polls
    for vote in user.votes:
        # Make sure the poll exists (hasn't just been deleted) and is closed
        if (
            vote.poll is not None
            and vote.poll not in polls_for_update
            and not vote.poll.closed
        ):
            polls_for_update.append(vote.poll)
        session.delete(vote)
    session.flush()

    for poll in polls_for_update:
        update_poll_messages(session, context.bot, poll)
    session.flush()

    user.delete()
    session.commit()

    context.query.message.chat.send_message(
        i18n.t("settings.user.deleted", locale=user.locale),
    )
