"""Admin related callback handler."""
import time

from pollbot.i18n import i18n
from pollbot.helper.plot import send_plots
from pollbot.helper.update import update_poll_messages
from pollbot.telegram.keyboard import get_admin_settings_keyboard
from pollbot.models import Poll
from pollbot.display.admin import stats


async def open_admin_settings(session, context, event):
    """Open the main menu."""
    keyboard = get_admin_settings_keyboard(context.user)
    await event.edit(
        stats(session),
        buttons=keyboard,
        parse_mode='Markdown',
        link_preview=False,
    )


async def update_all(session, context, event):
    """Update all polls."""
    updated = 0
    poll_count = session.query(Poll) \
        .filter(Poll.created.is_(True)) \
        .count()
    await event.respond(f'Updating {poll_count} polls')

    while updated < poll_count:
        polls = session.query(Poll) \
            .filter(Poll.created.is_(True)) \
            .order_by(Poll.id.desc()) \
            .offset(updated) \
            .limit(100) \
            .all()

        if updated % 500 == 0:
            await event.respond(f'Updated {updated} polls')
        updated += len(polls)

        for poll in polls:
            await update_poll_messages(session, poll)
            time.sleep(0.2)

    return "Done"


async def plot(session, context, event):
    """Plot interesting statistics."""
    await send_plots(session, event)
