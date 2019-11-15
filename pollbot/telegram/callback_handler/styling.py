"""Callback handler for poll styling."""
from pollbot.i18n import i18n
from pollbot.helper import poll_required
from pollbot.helper.enums import OptionSorting, UserSorting
from pollbot.helper.update import update_poll_messages
from pollbot.display.poll import get_poll_text
from pollbot.telegram.keyboard import get_styling_settings_keyboard


def send_styling_message(session, context):
    """Update the current styling menu message."""
    context.query.message.edit_text(
        text=get_poll_text(session, context.poll),
        parse_mode='markdown',
        reply_markup=get_styling_settings_keyboard(context.poll),
        disable_web_page_preview=True,
    )


@poll_required
def toggle_percentage(session, context, poll):
    """Toggle the visibility of the percentage bar."""
    if poll.anonymous and not poll.show_option_votes:
        context.query.message.chat.send_message(
            text=i18n.t('settings.anonymity_warning', locale=context.user.locale),
        )
        return
    poll.show_percentage = not poll.show_percentage

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


@poll_required
def toggle_option_votes(session, context, poll):
    """Toggle the visibility of the vote overview on an option."""
    if poll.anonymous and not poll.show_percentage:
        context.query.message.chat.send_message(
            text=i18n.t('settings.anonymity_warning', locale=context.user.locale),
        )
        return

    poll.show_option_votes = not poll.show_option_votes

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


@poll_required
def toggle_date_format(session, context, poll):
    """Switch between european and US date format."""
    poll.european_date_format = not poll.european_date_format
    poll.user.european_date_format = poll.european_date_format

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


@poll_required
def toggle_summerization(session, context, poll):
    """Toggle summarization of votes of a poll."""
    poll.summarize = not poll.summarize

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


@poll_required
def toggle_compact_buttons(session, context, poll):
    """Toggle the doodle poll button style."""
    poll.compact_buttons = not poll.compact_buttons

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


@poll_required
def set_option_order(session, context, poll):
    """Set the order in which options are listed."""
    option_sorting = OptionSorting(context.action)
    poll.option_sorting = option_sorting.name

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


@poll_required
def set_user_order(session, context, poll):
    """Set the order in which user are listed."""
    user_sorting = UserSorting(context.action)
    poll.user_sorting = user_sorting.name

    session.commit()
    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)
