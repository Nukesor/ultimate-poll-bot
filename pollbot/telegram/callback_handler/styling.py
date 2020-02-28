"""Callback handler for poll styling."""
from pollbot.i18n import i18n
from pollbot.helper import poll_required
from pollbot.helper.enums import OptionSorting, UserSorting
from pollbot.helper.update import update_poll_messages
from pollbot.display.poll.compilation import get_poll_text
from pollbot.telegram.keyboard import get_styling_settings_keyboard


async def send_styling_message(session, context, event):
    """Update the current styling menu message."""
    await event.edit(
        text=get_poll_text(session, context.poll),
        buttons=get_styling_settings_keyboard(context.poll),
        link_preview=False,
    )


@poll_required
async def toggle_percentage(session, context, event, poll):
    """Toggle the visibility of the percentage bar."""
    if poll.anonymous and not poll.show_option_votes:
        await event.respond(
            i18n.t('settings.anonymity_warning', locale=context.user.locale),
        )
        return
    poll.show_percentage = not poll.show_percentage

    session.commit()
    await update_poll_messages(session, poll)
    await send_styling_message(session, context, event)


@poll_required
async def toggle_option_votes(session, context, event, poll):
    """Toggle the visibility of the vote overview on an option."""
    if poll.anonymous and not poll.show_percentage:
        await event.respond(
            text=i18n.t('settings.anonymity_warning', locale=context.user.locale),
        )
        return

    poll.show_option_votes = not poll.show_option_votes

    session.commit()
    await update_poll_messages(session, poll)
    await send_styling_message(session, context, event)


@poll_required
async def toggle_date_format(session, context, event, poll):
    """Switch between european and US date format."""
    poll.european_date_format = not poll.european_date_format
    poll.user.european_date_format = poll.european_date_format

    session.commit()
    await update_poll_messages(session, poll)
    await send_styling_message(session, context, event)


@poll_required
async def toggle_summerization(session, context, event, poll):
    """Toggle summarization of votes of a poll."""
    poll.summarize = not poll.summarize

    session.commit()
    await update_poll_messages(session, poll)
    await send_styling_message(session, context, event)


@poll_required
async def toggle_compact_buttons(session, context, event, poll):
    """Toggle the doodle poll button style."""
    poll.compact_buttons = not poll.compact_buttons

    session.commit()
    await update_poll_messages(session, poll)
    await send_styling_message(session, context, event)


@poll_required
async def set_option_order(session, context, event, poll):
    """Set the order in which options are listed."""
    option_sorting = OptionSorting(context.action)
    poll.option_sorting = option_sorting.name

    session.commit()
    await update_poll_messages(session, poll)
    await send_styling_message(session, context, event)


@poll_required
async def set_user_order(session, context, event, poll):
    """Set the order in which user are listed."""
    user_sorting = UserSorting(context.action)
    poll.user_sorting = user_sorting.name

    session.commit()
    await update_poll_messages(session, poll)
    await send_styling_message(session, context, event)
