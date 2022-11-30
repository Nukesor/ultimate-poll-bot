"""Display helper for misc stuff."""
from typing import Tuple, Union

from sqlalchemy.orm.scoping import scoped_session
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

from pollbot.i18n import i18n
from pollbot.models import Poll
from pollbot.models.user import User
from pollbot.telegram.keyboard.management import get_poll_list_keyboard
from pollbot.telegram.keyboard.misc import get_help_keyboard


def get_help_text_and_keyboard(
    user: User, current_category: str
) -> Tuple[str, InlineKeyboardMarkup]:
    """Create the help message depending on the currently selected help category."""
    categories = [
        "creation",
        "settings",
        "notifications",
        "management",
        "languages",
        "bugs",
    ]

    text = i18n.t(f"misc.help.{current_category}", locale=user.locale)
    keyboard = get_help_keyboard(user, categories, current_category)

    return text, keyboard


def get_poll_list(
    session: scoped_session, user: User, offset: int, closed: bool = False
) -> Union[Tuple[str, InlineKeyboardMarkup], Tuple[str, None]]:
    """Get the a list of polls for the user."""
    polls = (
        session.query(Poll)
        .filter(Poll.user == user)
        .filter(Poll.created.is_(True))
        .filter(Poll.closed.is_(closed))
        .filter(Poll.delete.is_(None))
        .offset(offset)
        .limit(10)
        .all()
    )
    poll_count = (
        session.query(Poll)
        .filter(Poll.user == user)
        .filter(Poll.created.is_(True))
        .filter(Poll.closed.is_(closed))
        .count()
    )

    if len(polls) == 0 and closed:
        return i18n.t("list.no_closed_polls", locale=user.locale), None
    elif len(polls) == 0:
        return i18n.t("list.no_polls", locale=user.locale), None

    text = i18n.t("list.polls", locale=user.locale)
    keyboard = get_poll_list_keyboard(polls, closed, offset, poll_count)

    return text, keyboard
