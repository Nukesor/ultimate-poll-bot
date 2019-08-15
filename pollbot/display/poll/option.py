import math
import string
from datetime import date

from pollbot.helper.enums import PollType
from pollbot.helper import poll_allows_cumulative_votes
from pollbot.helper.vote import get_sorted_votes
from pollbot.helper.option import get_sorted_options, calculate_percentage
from .vote import get_vote_line


def get_option_information(session, poll, context):
    lines = []
    # Sort the options accordingly to the polls settings
    options = get_sorted_options(poll, context.total_user_count)

    # All options with their respective people percentage
    for index, option in enumerate(options):
        lines.append('')
        lines.append(get_option_line(session, option, index))
        if option.description is not None:
            lines.append(f'┆ _{option.description}_')

        if context.show_results and context.show_percentage:
            lines.append(get_percentage_line(option, context))

        # Add the names of the voters to the respective options
        if context.show_results and not context.anonymous and len(option.votes) > 0:
            # Sort the votes accordingly to the poll's settings
            votes = get_sorted_votes(poll, option.votes)
            for index, vote in enumerate(votes):
                vote_line = get_vote_line(poll, option, vote, index)
                lines.append(vote_line)

    return lines


def get_option_line(session, option, index):
    """Get the line with vote count for this option."""
    # Special formating for polls with european date format
    if option.is_date and option.poll.european_date_format:
        option_date = date.fromisoformat(option.name)
        option_name = option_date.strftime('%d.%m.%Y (%A)')
    elif option.is_date:
        option_date = date.fromisoformat(option.name)
        option_name = option_date.strftime('%Y-%m-%d (%A)')
    else:
        option_name = option.name

    prefix = ''
    if option.poll.poll_type == PollType.doodle.name:
        letters = string.ascii_letters
        prefix = f'{letters[index]}) '

    if len(option.votes) > 0 and option.poll.should_show_result():
        if poll_allows_cumulative_votes(option.poll):
            vote_count = sum([vote.vote_count for vote in option.votes])
        else:
            vote_count = len(option.votes)
        return f'┌ {prefix}*{option_name}* ({vote_count} votes)'
    else:
        return f'┌ {prefix}*{option_name}*'


def get_percentage_line(option, context):
    """Get the percentage line for each option."""
    percentage = calculate_percentage(option, context.total_user_count)
    filled_slots = math.floor(percentage/10)

    if len(option.votes) == 0 or option.poll.anonymous:
        line = '└ '
    else:
        line = '│ '

    line += filled_slots * '▬'
    line += (10-filled_slots) * '▭'
    line += f' ({percentage:.0f}%)'

    return ''.join(line)
