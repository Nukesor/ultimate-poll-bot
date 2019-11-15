"""Reply keyboards."""
import string
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.i18n import i18n
from pollbot.config import config
from pollbot.helper import poll_allows_cumulative_votes
from pollbot.helper.enums import (
    CallbackType,
    CallbackResult,
    OptionSorting,
    PollType,
    StartAction,
)
from pollbot.telegram.keyboard import get_start_button_payload
from pollbot.helper.option import get_sorted_options

from .management import get_back_to_management_button

IGNORE_PAYLOAD = f'{CallbackType.ignore.value}:0:0'


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
            buttons.append([InlineKeyboardButton(
                i18n.t('keyboard.new_option', locale=poll.locale), url=url)])

    # Add a button for to showing the summary, if the poll is too long for a single message
    if summary:
        payload = get_start_button_payload(poll, StartAction.show_results)
        bot_name = config['telegram']['bot_name']
        url = f'http://t.me/{bot_name}?start={payload}'
        row = [InlineKeyboardButton(i18n.t('keyboard.show_results', locale=poll.locale), url=url)]

    # Add a button to go back to the management interface (admin overview)
    if show_back:
        buttons.append([get_back_to_management_button(poll)])

    return InlineKeyboardMarkup(buttons)


def get_vote_buttons(poll, user=None, show_back=False):
    """Get the keyboard for actual voting."""
    locale = poll.locale

    if poll_allows_cumulative_votes(poll):
        buttons = get_cumulative_buttons(poll)
    elif poll.poll_type == PollType.doodle.name:
        buttons = get_doodle_buttons(poll)
    elif poll.is_stv():
        buttons = get_stv_buttons(poll, user)
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
        buttons.append([InlineKeyboardButton(text, callback_data=payload)])

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
            InlineKeyboardButton(f'－ {option_name}', callback_data=no_payload),
            InlineKeyboardButton(f'＋ {option_name}', callback_data=yes_payload),
        ])

    return buttons


def get_stv_buttons(poll, user):
    """Create the keyboard for stv poll. Only show the deeplink, if not in a direct conversation."""
    if user is None:
        bot_name = config['telegram']['bot_name']
        payload = get_start_button_payload(poll, StartAction.vote)
        url = f'http://t.me/{bot_name}?start={payload}'
        buttons = [[InlineKeyboardButton(
            i18n.t('keyboard.vote', locale=poll.locale), url=url)]]

        return buttons

    buttons = []
    options = get_sorted_options(poll)
    vote_button_type = CallbackType.vote.value
    vote_increase = CallbackResult.increase_priority.value
    vote_decrease = CallbackResult.decrease_priority.value
    for index, option in enumerate(options):
        if not poll.compact_buttons:
            name_row = [
                InlineKeyboardButton(
                    f"{index + 1}) {option.name}",
                    callback_data=IGNORE_PAYLOAD
                )
            ]
            buttons.append(name_row)
        name_hint_payload = f'{CallbackType.show_option_name.value}:{poll.id}:{option.id}'
        increase_payload = f'{vote_button_type}:{option.id}:{vote_increase}'
        decrease_payload = f'{vote_button_type}:{option.id}:{vote_decrease}'
        vote_row = [
            InlineKeyboardButton(f"{index + 1}.", callback_data=name_hint_payload),
            InlineKeyboardButton('▲', callback_data=increase_payload),
            InlineKeyboardButton('▼', callback_data=decrease_payload),
        ]
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
    letters = string.ascii_lowercase + '123456789'
    for index, option in enumerate(options):
        name_hint_payload = f'{show_option_name}:{poll.id}:{option.id}'
        yes_payload = f'{vote_button_type}:{option.id}:{vote_yes}'
        maybe_payload = f'{vote_button_type}:{option.id}:{vote_maybe}'
        no_payload = f'{vote_button_type}:{option.id}:{vote_no}'

        # If we don't have the compact button view, display the option name on it's own button row
        if not poll.compact_buttons:
            option_row = [InlineKeyboardButton(option.get_formatted_name(),
                                               callback_data=name_hint_payload)]
            buttons.append(option_row)
            option_row = []
        else:
            option_row = [InlineKeyboardButton(f'{letters[index]})', callback_data=name_hint_payload)]

        vote_row = [
            InlineKeyboardButton('✅', callback_data=yes_payload),
            InlineKeyboardButton('❔', callback_data=maybe_payload),
            InlineKeyboardButton('❌', callback_data=no_payload),
        ]

        buttons.append(option_row + vote_row)

    return buttons
