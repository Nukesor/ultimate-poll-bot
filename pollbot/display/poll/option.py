"""Poll text compilation for options."""
import math

from pollbot.helper.enums import PollType
from pollbot.helper import poll_allows_cumulative_votes
from pollbot.helper.option import get_sorted_options, calculate_percentage
from pollbot.display.poll.indices import get_option_indices
from .vote import get_vote_lines, get_doodle_vote_lines


def get_option_information(session, poll, context, summarize):
    """Compile all information about a poll option."""
    lines = []
    # Sort the options accordingly to the polls settings
    options = get_sorted_options(poll, context.total_user_count)

    # All options with their respective people percentage
    for index, option in enumerate(options):
        lines.append('')
        lines.append(get_option_line(session, option, index))
        if option.description is not None:
            lines.append(f'┆ __{option.description}__')

        if context.show_results and context.show_percentage:
            lines.append(get_percentage_line(option, context))

        # Add the names of the voters to the respective options
        if context.show_results and not context.anonymous and len(option.votes) > 0 and not poll.is_priority():
            # Sort the votes accordingly to the poll's settings
            if poll.poll_type == PollType.doodle.name:
                lines += get_doodle_vote_lines(poll, option, summarize)
            else:
                lines += get_vote_lines(poll, option, summarize)

    return lines


def get_option_line(session, option, index):
    """Get the line with vote count for this option."""
    # Special formating for polls with European date format
    option_name = option.get_formatted_name()

    prefix = ''
    if option.poll.poll_type in [PollType.doodle.name, PollType.priority.name]:
        indices = get_option_indices(option.poll.options)
        prefix = f'{indices[index]}) '

    if len(option.votes) > 0 and \
       option.poll.should_show_result() and \
       option.poll.show_option_votes and \
       not option.poll.is_priority():
        if poll_allows_cumulative_votes(option.poll):
            vote_count = sum([vote.vote_count for vote in option.votes])
        else:
            vote_count = len(option.votes)
        return f'┌ {prefix}**{option_name}** ({vote_count} votes)'
    else:
        return f'┌ {prefix}**{option_name}**'


def get_percentage_line(option, context):
    """Get the percentage line for each option."""

    poll = option.poll
    if len(option.votes) == 0 or poll.anonymous or poll.is_priority():
        line = '└ '
    else:
        line = '│ '


    if not poll.is_priority():
        percentage = calculate_percentage(option, context.total_user_count)
        filled_slots = math.floor(percentage / 10)
        line += filled_slots * '▬'
        line += (10 - filled_slots) * '▭'
        line += f' ({percentage:.0f}%)'
    else:
        option_count = len(poll.options)
        points = sum([option_count - vote.priority for vote in option.votes])
        line += f' {points} Points'

    return ''.join(line)
