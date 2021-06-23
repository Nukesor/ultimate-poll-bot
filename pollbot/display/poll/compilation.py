from typing import List, Optional, Tuple

from sqlalchemy.orm.scoping import scoped_session
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

from pollbot.display.poll import Context
from pollbot.i18n import i18n
from pollbot.models.poll import Poll
from pollbot.models.user import User
from pollbot.telegram.keyboard.vote import get_vote_keyboard

from .option import get_option_information
from .vote import get_remaining_votes_lines, get_vote_information_line


def get_poll_text_and_vote_keyboard(
    session: scoped_session,
    poll: Poll,
    user: Optional[User] = None,
    show_back: bool = False,
) -> Tuple[str, InlineKeyboardMarkup]:
    """Get the text and the vote keyboard."""
    text, summarize = get_poll_text_and_summarize(
        session,
        poll,
    )

    keyboard = get_vote_keyboard(poll, user, show_back, summary=summarize)

    return text, keyboard


def get_poll_text(session: scoped_session, poll: Poll) -> str:
    """Only get the poll text."""
    text, _ = get_poll_text_and_summarize(session, poll)
    return text


def get_poll_text_and_summarize(
    session: scoped_session, poll: Poll
) -> Tuple[str, bool]:
    """Get the poll text and vote keyboard."""
    summarize = poll.permanently_summarized or poll.summarize

    # Always summarize
    if summarize:
        lines = compile_poll_text(session, poll, summarize=summarize)
        text = "\n".join(lines)

    else:
        # We don't know if we should summarize yet.
        # Don't use the summarized version.
        lines = compile_poll_text(session, poll)
        text = "\n".join(lines)

        # If the text is too long, summarize it.
        if len(text) > 4000:
            poll.permanently_summarize = True
            lines = compile_poll_text(session, poll, summarize=summarize)
            text = "\n".join(lines)

    # The text is still too long after summarization
    # Print a debug text
    if len(text) > 4000:
        text = i18n.t("misc.too_long", locale=poll.locale)
        poll.permanently_summarized = True

    return text, summarize


def compile_poll_text(
    session: scoped_session, poll: Poll, summarize: bool = False
) -> List[str]:
    """Create the text of the poll."""
    context = Context(session, poll)

    # Name and description
    lines = []
    lines.append(f"✉️ *{poll.name}*")

    if poll.description is not None:
        lines.append(f"_{poll.description}_")

    # Anonymity information
    if not context.show_results or context.anonymous:
        lines.append("")
    if context.anonymous:
        anonymous = i18n.t("poll.anonymous", locale=poll.locale)
        lines.append(f"_{anonymous}_")
        if context.show_results:
            lines.append(i18n.t("poll.anonymous_warning", locale=poll.locale))
    if not context.show_results:
        not_visible = i18n.t("poll.results_not_visible", locale=poll.locale)
        lines.append(f"_{not_visible}_")

    lines += get_option_information(session, poll, context, summarize)
    lines.append("")

    if context.limited_votes:
        lines.append(
            i18n.t("poll.vote_times", locale=poll.locale, amount=poll.number_of_votes)
        )

    # Total user count information
    information_line = get_vote_information_line(poll, context)
    if information_line is not None:
        lines.append(information_line)

    if (
        context.show_results
        and not context.anonymous
        and context.limited_votes
        and not summarize
    ):
        remaining_votes = get_remaining_votes_lines(session, poll)
        lines += remaining_votes

    if poll.due_date is not None:
        lines.append(
            i18n.t("poll.due", locale=poll.locale, date=poll.get_formatted_due_date())
        )

    if not poll.closed and poll.compact_buttons:
        lines.append("")
        lines.append(i18n.t("poll.doodle_help", locale=poll.locale))
        lines.append("")

    # Notify users that poll is closed
    if poll.closed:
        lines.append(i18n.t("poll.closed", locale=poll.locale))

    return lines
