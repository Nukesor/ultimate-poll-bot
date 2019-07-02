"""Reply keyboards."""
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from pollbot.config import config
from pollbot.helper import poll_allows_cumulative_votes
from pollbot.helper.enums import (
    CallbackType,
    CallbackResult,
    OptionSorting,
)
from pollbot.helper.display import get_sorted_options

from .management import get_back_to_management_button


def get_vote_keyboard(poll, show_back=False):
    """Get the keyboard for actual voting."""
    if poll.closed:
        return None

    if poll_allows_cumulative_votes(poll):
        buttons = get_cumulative_buttons(poll)
    else:
        buttons = get_normal_buttons(poll)

    if poll.allow_new_options:
        bot_name = config['telegram']['bot_name']
        url = f'http://t.me/{bot_name}?start={poll.uuid}'
        buttons.append([InlineKeyboardButton(text='Add a new option.', url=url)])

    if show_back:
        buttons.append([get_back_to_management_button(poll)])

    return InlineKeyboardMarkup(buttons)


def get_normal_buttons(poll):
    """Get the normal keyboard with one button per option."""
    buttons = []
    vote_button_type = CallbackType.vote.value

    options = poll.options
    if poll.option_sorting == OptionSorting.option_name.name:
        options = get_sorted_options(poll)

    for option in options:
        option_name = option.get_formatted_name()

        result = CallbackResult.vote.value
        payload = f'{vote_button_type}:{option.id}:{result}'
        if poll.should_show_result():
            text = f'{option_name} ({len(option.votes)} votes)'
        else:
            text = f'{option_name}'
        buttons.append([InlineKeyboardButton(text=text, callback_data=payload)])

    return buttons


def get_cumulative_buttons(poll):
    """Get the normal keyboard with one button per option."""
    vote_button_type = CallbackType.vote.value
    vote_yes = CallbackResult.vote_yes.value
    vote_no = CallbackResult.vote_no.value

    options = poll.options
    if poll.option_sorting == OptionSorting.option_name:
        options = get_sorted_options(poll)

    buttons = []
    for option in options:
        option_name = option.get_formatted_name()

        yes_payload = f'{vote_button_type}:{option.id}:{vote_yes}'
        no_payload = f'{vote_button_type}:{option.id}:{vote_no}'
        buttons.append([
            InlineKeyboardButton(text=f'－ {option_name}', callback_data=no_payload),
            InlineKeyboardButton(text=f'＋ {option_name}', callback_data=yes_payload),
        ])

    return buttons
