"""Poll text compilation for options."""
import math
from typing import Any, List, Union

from sqlalchemy.orm.scoping import scoped_session
from telegram.chat import Chat

from pollbot.display.poll import Context
from pollbot.display.poll.indices import get_option_indices
from pollbot.enums import ExpectedInput, PollType
from pollbot.exceptions import RollbackException
from pollbot.i18n import i18n
from pollbot.models import Option, Poll
from pollbot.poll.helper import poll_allows_cumulative_votes
from pollbot.poll.option import calculate_percentage, get_sorted_options
from pollbot.telegram.keyboard.creation import get_options_entered_keyboard

from .vote import get_doodle_vote_lines, get_vote_lines


def next_option(tg_chat: Chat, poll: Poll, added_options: List[str]) -> None:
    """Send the options message during the creation.

    This function also has a failsafe in it, that rollbacks the entire transaction,
    if the message with the added options is too long to be displayed in telegram.
    """
    locale = poll.user.locale
    poll.user.expected_input = ExpectedInput.options.name
    keyboard = get_options_entered_keyboard(poll)

    if len(added_options) == 1:
        text = i18n.t(
            "creation.option.single_added", locale=locale, option=added_options[0]
        )
    else:
        text = i18n.t("creation.option.multiple_added", locale=locale)
        for option in added_options:
            text += f"\n*{option}*"
        text += "\n\n" + i18n.t("creation.option.next", locale=locale)

    if len(text) > 3800:
        error_message = i18n.t("misc.over_4000", locale=locale)
        raise RollbackException(error_message)

    tg_chat.send_message(text, reply_markup=keyboard, parse_mode="Markdown")


def get_option_information(
    session: scoped_session, poll: Poll, context: Context, summarize: bool
) -> List[Union[Any, str]]:
    """Compile all information about a poll option."""
    lines = []
    # Sort the options accordingly to the polls settings
    options = get_sorted_options(poll, context.total_user_count)

    # All options with their respective people percentage
    for index, option in enumerate(options):
        lines.append("")
        lines.append(get_option_line(session, option, index))
        if option.description is not None:
            lines.append(f"┆ _{option.description}_")

        if context.show_results and context.show_percentage:
            lines.append(get_percentage_line(option, context))

        # Add the names of the voters to the respective options
        if (
            context.show_results
            and not context.anonymous
            and len(option.votes) > 0
            and not poll.is_priority()
        ):
            # Sort the votes accordingly to the poll's settings
            if poll.poll_type == PollType.doodle.name:
                lines += get_doodle_vote_lines(poll, option, summarize)
            else:
                lines += get_vote_lines(poll, option, summarize)

    return lines


def get_option_line(session: scoped_session, option: Option, index: int) -> str:
    """Get the line with vote count for this option."""
    # Special formating for polls with European date format
    option_name = option.get_formatted_name()

    prefix = ""
    if option.poll.poll_type in [PollType.doodle.name, PollType.priority.name]:
        indices = get_option_indices(option.poll.options)
        prefix = f"{indices[index]}) "

    if (
        len(option.votes) > 0
        and option.poll.should_show_result()
        and option.poll.show_option_votes
        and not option.poll.is_priority()
    ):
        if poll_allows_cumulative_votes(option.poll):
            vote_count = sum([vote.vote_count for vote in option.votes])
        else:
            vote_count = len(option.votes)
        return f"┌ {prefix}*{option_name}* ({vote_count} votes)"
    else:
        return f"┌ {prefix}*{option_name}*"


def get_percentage_line(option: Option, context: Context) -> str:
    """Get the percentage line for each option."""

    poll = option.poll
    if len(option.votes) == 0 or poll.anonymous or poll.is_priority():
        line = "└ "
    else:
        line = "│ "

    if not poll.is_priority():
        percentage = calculate_percentage(option, context.total_user_count)
        filled_slots = math.floor(percentage / 10)
        line += filled_slots * "▬"
        line += (10 - filled_slots) * "▭"
        line += f" ({round(percentage)}%)"
    else:
        option_count = len(poll.options)
        points = sum([option_count - vote.priority for vote in option.votes])
        line += f" {points} Points"

    return "".join(line)
