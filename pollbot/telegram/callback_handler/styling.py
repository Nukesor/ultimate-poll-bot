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
    poll = poll
    poll.show_percentage = not poll.show_percentage

    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


@poll_required
def toggle_date_format(session, context, poll):
    """Switch between european and US date format."""
    poll.european_date_format = not poll.european_date_format
    poll.user.european_date_format = poll.european_date_format

    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


@poll_required
def toggle_summerization(session, context, poll):
    """Toggle summarization of votes of a poll."""
    poll.summarize = not poll.summarize

    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


@poll_required
def set_option_order(session, context, poll):
    """Set the order in which options are listed."""
    option_sorting = OptionSorting(context.action)
    poll.option_sorting = option_sorting.name

    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)


@poll_required
def set_user_order(session, context, poll):
    """Set the order in which user are listed."""
    user_sorting = UserSorting(context.action)
    poll.user_sorting = user_sorting.name

    update_poll_messages(session, context.bot, poll)
    send_styling_message(session, context)
