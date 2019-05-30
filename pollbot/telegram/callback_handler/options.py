"""Callback functions needed during creation of a Poll."""
from pollbot.helper.display import update_poll_messages

from pollbot.helper.display import get_options_text
from pollbot.telegram.keyboard import (
    get_anonymization_confirmation_keyboard,
    get_options_keyboard,
    get_option_sorting_keyboard,
)
from pollbot.helper.enums import OptionSorting, UserSorting


def show_anonymization_confirmation(session, context):
    """Show the delete confirmation message."""
    context.query.message.edit_text(
        'Do you really want to anonymize this poll?\n⚠️ This action is unrevertable. ⚠️',
        reply_markup=get_anonymization_confirmation_keyboard(context.poll),
    )


def make_anonymous(session, context):
    """Change the anonymity settings of a poll."""
    context.poll.anonymous = True

    context.query.message.edit_text(
        get_options_text(context.poll),
        parse_mode='markdown',
        reply_markup=get_options_keyboard(context.poll)
    )

    update_poll_messages(session, context.bot, context.poll)


def show_sorting_menu(session, context):
    """Show the menu for sorting settings."""
    context.query.message.edit_reply_markup(
        parse_mode='markdown',
        reply_markup=get_option_sorting_keyboard(context.poll)
    )


def set_user_order(session, context):
    """Set the order in which user are listed."""
    user_sorting = UserSorting(context.action)
    context.poll.user_sorting = user_sorting.name

    context.query.message.edit_text(
        text=get_options_text(context.poll),
        parse_mode='markdown',
        reply_markup=get_option_sorting_keyboard(context.poll)
    )
    update_poll_messages(session, context.bot, context.poll)


def set_option_order(session, context):
    """Set the order in which options are listed."""
    option_sorting = OptionSorting(context.action)
    context.poll.option_sorting = option_sorting.name

    context.query.message.edit_text(
        text=get_options_text(context.poll),
        parse_mode='markdown',
        reply_markup=get_option_sorting_keyboard(context.poll)
    )

    update_poll_messages(session, context.bot, context.poll)
