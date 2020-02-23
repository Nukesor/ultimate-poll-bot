"""Reply keyboards."""
from telethon import Button
from sqlalchemy.orm import joinedload

from pollbot.models import Vote
from pollbot.i18n import i18n
from pollbot.config import config
from pollbot.helper import poll_allows_cumulative_votes
from pollbot.db import get_session
from pollbot.helper.enums import (
    CallbackType,
    CallbackResult,
    OptionSorting,
    PollType,
    StartAction,
)
from pollbot.telegram.keyboard import get_start_button_payload
from pollbot.helper.option import get_sorted_options
from pollbot.display.poll.indices import get_option_indices

from .management import get_back_to_management_button



def get_vote_keyboard(poll, user, show_back=False, summary=False):
    """Get a plain vote keyboard."""
    buttons = []

    # If the poll is not closed yet, add the vote buttons and the button
    # to add new options for new users (if enabled)
    if not poll.closed:
        buttons = get_vote_buttons(poll, user, show_back)

        if poll.allow_new_options:
            bot_name = config['telegram']['bot_name']
            payload = get_start_button_payload(poll, StartAction.new_option)
            url = f'http://t.me/{bot_name}?start={payload}'
            buttons.append([Button.url(i18n.t('keyboard.new_option', locale=poll.locale), url)])

    # Add a button for to showing the summary, if the poll is too long for a single message
    if summary:
        payload = get_start_button_payload(poll, StartAction.show_results)
        bot_name = config['telegram']['bot_name']
        url = f'http://t.me/{bot_name}?start={payload}'
        row = [Button.url(i18n.t('keyboard.show_results', locale=poll.locale), url)]
        buttons.append(row)

    # Add a button to go back to the management interface (admin overview)
    if show_back:
        buttons.append([get_back_to_management_button(poll)])

    return buttons


def get_vote_buttons(poll, user=None, show_back=False):
    """Get the keyboard for actual voting."""
    if poll_allows_cumulative_votes(poll):
        buttons = get_cumulative_buttons(poll)
    elif poll.poll_type == PollType.doodle.name:
        buttons = get_doodle_buttons(poll)
    elif poll.is_priority():
        buttons = get_priority_buttons(poll, user)
    else:
        buttons = get_normal_buttons(poll)

    return buttons


def get_normal_buttons(poll):
    """Get the normal keyboard with one vote button per option."""
    buttons = []
    vote_button_type = CallbackType.vote.value

    options = poll.options
    if poll.option_sorting == OptionSorting.option_name.name:
        options = get_sorted_options(poll)

    for option in options:
        option_name = option.get_formatted_name()

        result = CallbackResult.vote.value
        payload = f'{vote_button_type}:{option.id}:{result}'
        if poll.should_show_result() and poll.show_option_votes:
            text = i18n.t('keyboard.vote_with_count',
                          option_name=option_name,
                          count=len(option.votes),
                          locale=poll.locale)
        else:
            text = option_name
        buttons.append([Button.inline(text, data=payload)])

    return buttons


def get_cumulative_buttons(poll):
    """Get the cumulative keyboard with two buttons per option."""
    vote_button_type = CallbackType.vote.value
    vote_yes = CallbackResult.yes.value
    vote_no = CallbackResult.no.value

    options = poll.options
    if poll.option_sorting == OptionSorting.option_name:
        options = get_sorted_options(poll)

    buttons = []
    for option in options:
        option_name = option.get_formatted_name()

        yes_payload = f'{vote_button_type}:{option.id}:{vote_yes}'
        no_payload = f'{vote_button_type}:{option.id}:{vote_no}'
        buttons.append([
            Button.inline(f'－ {option_name}', data=no_payload),
            Button.inline(f'＋ {option_name}', data=yes_payload),
        ])

    return buttons


def get_priority_buttons(poll, user):
    """Create the keyboard for priority poll. Only show the deeplink, if not in a direct conversation."""
    if user is None:
        bot_name = config['telegram']['bot_name']
        payload = get_start_button_payload(poll, StartAction.vote)
        url = f'http://t.me/{bot_name}?start={payload}'
        buttons = [[Button.url(i18n.t('keyboard.vote', locale=poll.locale), url)]]

        return buttons

    buttons = []
    options = get_sorted_options(poll)
    vote_button_type = CallbackType.vote.value
    vote_increase = CallbackResult.increase_priority.value
    vote_decrease = CallbackResult.decrease_priority.value
    session = get_session()
    votes = session.query(Vote) \
        .filter(Vote.poll == poll) \
        .filter(Vote.user == user) \
        .order_by(Vote.priority.asc()) \
        .options(joinedload(Vote.poll_option)) \
        .all()

    ignore_payload = f'{CallbackType.ignore.value}:0:0'
    indices = get_option_indices(options)
    for index, vote in enumerate(votes):
        option = vote.poll_option
        if not poll.compact_buttons:
            name_row = [
                Button.inline(f"{option.name}", data=ignore_payload)
            ]
            buttons.append(name_row)
        name_hint_payload = f'{CallbackType.show_option_name.value}:{poll.id}:{option.id}'
        increase_payload = f'{vote_button_type}:{option.id}:{vote_increase}'
        decrease_payload = f'{vote_button_type}:{option.id}:{vote_decrease}'

        vote_row = []
        if poll.compact_buttons:
            vote_row.append(Button.inline(f"{indices[index]})", data=name_hint_payload))

        if index != len(votes) - 1:
            vote_row.append(Button.inline('▼', data=decrease_payload))
        else:
            vote_row.append(Button.inline(' ', data=ignore_payload))

        if index != 0:
            vote_row.append(Button.inline('▲', data=increase_payload))
        else:
            vote_row.append(Button.inline(' ', data=ignore_payload))

        buttons.append(vote_row)
    return buttons


def get_doodle_buttons(poll):
    """Get the doodle keyboard with yes, maybe and no button per option."""
    show_option_name = CallbackType.show_option_name.value
    vote_button_type = CallbackType.vote.value
    vote_yes = CallbackResult.yes.value
    vote_maybe = CallbackResult.maybe.value
    vote_no = CallbackResult.no.value

    options = get_sorted_options(poll)

    buttons = []
    indices = get_option_indices(options)

    for index, option in enumerate(options):
        name_hint_payload = f'{show_option_name}:{poll.id}:{option.id}'
        yes_payload = f'{vote_button_type}:{option.id}:{vote_yes}'
        maybe_payload = f'{vote_button_type}:{option.id}:{vote_maybe}'
        no_payload = f'{vote_button_type}:{option.id}:{vote_no}'

        # If we don't have the compact button view, display the option name on it's own button row
        if not poll.compact_buttons:
            option_row = [Button.inline(option.get_formatted_name(), data=name_hint_payload)]
            buttons.append(option_row)
            option_row = []
        else:
            option_row = [Button.inline(f'{indices[index]})', data=name_hint_payload)]

        vote_row = [
            Button.inline('✅', data=yes_payload),
            Button.inline('❔', data=maybe_payload),
            Button.inline('❌', data=no_payload),
        ]

        buttons.append(option_row + vote_row)

    return buttons
