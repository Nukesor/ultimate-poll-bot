"""Admin related callback handler."""
import time

from sqlalchemy.orm.scoping import scoped_session

from pollbot.display.admin import stats
from pollbot.helper.plot import send_plots
from pollbot.models import Poll
from pollbot.poll.update import update_poll_messages
from pollbot.telegram.callback_handler.context import CallbackContext
from pollbot.telegram.keyboard.user import get_admin_settings_keyboard


def open_admin_settings(session: scoped_session, context: CallbackContext) -> None:
    """Open the main menu."""
    keyboard = get_admin_settings_keyboard(context.user)
    context.query.message.edit_text(
        stats(session),
        reply_markup=keyboard,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )


def update_all(session: scoped_session, context: CallbackContext) -> str:
    """Update all polls."""
    chat = context.query.message.chat

    updated = 0
    poll_count = session.query(Poll).filter(Poll.created.is_(True)).count()
    chat.send_message(f"Updating {poll_count} polls")
    print(f"Updating {poll_count} polls")

    while updated < poll_count:
        polls = (
            session.query(Poll)
            .filter(Poll.created.is_(True))
            .order_by(Poll.id.desc())
            .offset(updated)
            .limit(100)
            .all()
        )

        if updated % 500 == 0:
            chat.send_message(f"Updated {updated} polls")
        updated += len(polls)

        for poll in polls:
            update_poll_messages(session, context.bot, poll)
            time.sleep(0.2)

    return "Done"


def plot(session: scoped_session, context: CallbackContext) -> None:
    """Plot interesting statistics."""
    send_plots(session, context.query.message.chat)
