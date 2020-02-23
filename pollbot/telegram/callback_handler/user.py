"""User related callback handler."""
from pollbot.i18n import i18n
from pollbot.helper.update import remove_poll_messages
from pollbot.display.creation import get_init_text
from pollbot.display.settings import get_user_settings_text
from pollbot.display.misc import (
    get_poll_list,
    get_help_text_and_keyboard,
)
from pollbot.models import Poll
from pollbot.telegram.keyboard import (
    get_main_keyboard,
    get_init_keyboard,
    get_user_settings_keyboard,
    get_user_language_keyboard,
    get_cancel_creation_keyboard,
    get_donations_keyboard,
    get_delete_all_confirmation_keyboard,
)


async def open_main_menu(session, context, event):
    """Open the main menu."""
    keyboard = get_main_keyboard(context.user)
    await event.edit(
        i18n.t('misc.start', locale=context.user.locale),
        buttons=keyboard,
        link_preview=False,
    )


async def open_user_settings(session, context, event):
    """Open the user settings."""
    keyboard = get_user_settings_keyboard(context.user)
    text = get_user_settings_text(context.user)
    await event.edit(text, buttons=keyboard)


async def open_language_menu(session, context, event):
    """Open the user language selection menu."""
    keyboard = get_user_language_keyboard(context.user)
    await event.edit(
        i18n.t('settings.change_language', locale=context.user.locale),
        buttons=keyboard,
    )


async def list_polls(session, context, event):
    """List all open polls of a user."""
    text, keyboard = get_poll_list(session, context.user)
    await event.respond(text, buttons=keyboard)


async def list_closed_polls(session, context, event):
    """List all open polls of a user."""
    text, keyboard = get_poll_list(session, context.user, closed=True)
    await event.respond(text, buttons=keyboard)


async def open_donation(session, context, event):
    """Open the donations text."""
    await event.edit(
        i18n.t('misc.donation', locale=context.user.locale),
        buttons=get_donations_keyboard(context.user),
    )


async def open_help(session, context, event):
    """Open the donations text."""
    text, keyboard = get_help_text_and_keyboard(context.user, 'intro')
    await event.edit(text, buttons=keyboard, link_preview=False)


async def init_poll(session, context, event):
    """Start the creation of a new poll."""
    user = context.user
    if user.current_poll is not None and not user.current_poll.created:
        await event.respond(
            i18n.t('creation.already_creating', locale=user.locale),
            buttons=get_cancel_creation_keyboard(user.current_poll))
        return

    poll = Poll.create(user, session)
    text = get_init_text(poll)
    keyboard = get_init_keyboard(poll)

    await event.respond(text, buttons=keyboard, link_preview=False)


async def toggle_notification(session, context, event):
    """Toggle the notification settings of the user."""
    user = context.user
    user.notifications_enabled = not user.notifications_enabled
    session.commit()
    await open_user_settings(session, context, event)


async def change_user_language(session, context, event):
    """Open the language picker."""
    context.user.locale = context.action
    session.commit()
    await open_user_settings(session, context, event)
    return i18n.t('user.language_changed', locale=context.user.locale)


async def delete_all_confirmation(session, context, event):
    keyboard = get_delete_all_confirmation_keyboard(context.user)
    await event.edit(
        i18n.t('settings.user.delete_all_confirmation',
               locale=context.user.locale),
        buttons=keyboard,
    )


async def delete_closed_confirmation(session, context, event):
    keyboard = get_delete_all_confirmation_keyboard(context.user, closed=True)
    await event.edit(
        i18n.t('settings.user.delete_all_confirmation',
               locale=context.user.locale),
        parse_mode='markdown',
        buttons=keyboard,
    )


async def delete_all(session, context, event):
    """Delete all polls of the user."""
    for poll in context.user.polls:
        await remove_poll_messages(session, context, event.bot, poll)
        session.delete(poll)
        session.commit()

    await open_user_settings(session, context, event)
    return i18n.t('deleted.polls', locale=context.user.locale)


async def delete_closed(session, context, event):
    """Delete all closed polls of the user."""
    for poll in context.user.polls:
        if poll.closed:
            await remove_poll_messages(session, context, poll)
            session.delete(poll)
            session.commit()

    await open_user_settings(session, context, event)
    return i18n.t('deleted.closed_polls', locale=context.user.locale)
