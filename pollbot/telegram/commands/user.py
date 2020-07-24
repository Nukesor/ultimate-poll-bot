from pollbot.display.settings import get_user_settings_text
from pollbot.i18n import i18n
from pollbot.telegram.keyboard.user import (
    get_delete_user_confirmation_keyboard,
    get_user_settings_keyboard,
)
from pollbot.telegram.session import message_wrapper
from telegram.ext import run_async


@run_async
@message_wrapper()
def open_user_settings_command(bot, update, session, user):
    """Open the settings menu for the user."""
    update.message.chat.send_message(
        get_user_settings_text(user),
        reply_markup=get_user_settings_keyboard(user),
        parse_mode="markdown",
    )


@run_async
@message_wrapper()
def stop(bot, update, session, user):
    """Stop the user."""
    user.started = False
    session.commit()
    update.message.chat.send_message(
        i18n.t("misc.stop", locale=user.locale), parse_mode="markdown",
    )


@run_async
@message_wrapper()
def delete_me(bot, update, session, user):
    """Show the confirmation message before deleting the uesr."""
    update.message.chat.send_message(
        i18n.t("misc.deletion_warning", locale=user.locale),
        reply_markup=get_delete_user_confirmation_keyboard(user),
        parse_mode="markdown",
    )
