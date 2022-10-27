"""Reply keyboards."""
from typing import Any, List, Optional, Union

from sqlalchemy.orm import joinedload
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from pollbot.config import config
from pollbot.db import get_session
from pollbot.display.poll.indices import get_option_indices
from pollbot.enums import CallbackResult, CallbackType, PollType, StartAction
from pollbot.i18n import i18n
from pollbot.models import Vote
from pollbot.models.poll import Poll
from pollbot.models.user import User
from pollbot.poll.helper import poll_allows_cumulative_votes
from pollbot.poll.option import get_sorted_options
from pollbot.telegram.keyboard.helper import get_start_button_payload

from .management import get_back_to_management_button

IGNORE_PAYLOAD = f"{CallbackType.ignore.value}:0:0"


def get_vote_keyboard(
    poll: Poll, user: Optional[User], show_back: bool = False, summary: bool = False
) -> InlineKeyboardMarkup:
    """Get a plain vote keyboard."""
    buttons = []

    # If the poll is not closed yet, add the vote buttons and the button
    # to add new options for new users (if enabled)
    if not poll.closed:
        buttons = get_vote_buttons(poll, user, show_back)

        bot_name = config["telegram"]["bot_name"]
        if poll.allow_new_options:
            payload = get_start_button_payload(poll, StartAction.new_option)
            url = f"http://t.me/{bot_name}?start={payload}"
            buttons.append(
                [
                    InlineKeyboardButton(
                        i18n.t("keyboard.new_option", locale=poll.locale), url=url
                    )
                ]
            )
        if poll.allow_sharing:
            payload = get_start_button_payload(poll, StartAction.share_poll)
            url = f"http://t.me/{bot_name}?start={payload}"
            buttons.append(
                [
                    InlineKeyboardButton(
                        i18n.t("keyboard.share", locale=poll.locale), url=url
                    )
                ]
            )

    # Add a button for to showing the summary, if the poll is too long for a single message
    if summary:
        payload = get_start_button_payload(poll, StartAction.show_results)
        bot_name = config["telegram"]["bot_name"]
        url = f"http://t.me/{bot_name}?start={payload}"
        row = [
            InlineKeyboardButton(
                i18n.t("keyboard.show_results", locale=poll.locale), url=url
            )
        ]
        buttons.append(row)

    # Add a button to go back to the management interface (admin overview)
    if show_back:
        buttons.append([get_back_to_management_button(poll)])

    return InlineKeyboardMarkup(buttons)


def get_vote_buttons(
    poll: Poll, user: Optional[User] = None, show_back: bool = False
) -> List[Union[List[InlineKeyboardButton], Any]]:
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


def get_normal_buttons(poll: Poll) -> List[Union[List[InlineKeyboardButton], Any]]:
    """Get the normal keyboard with one vote button per option."""
    buttons = []
    vote_button_type = CallbackType.vote.value

    options = poll.options

    for option in options:
        option_name = option.get_formatted_name()

        result = CallbackResult.vote.value
        payload = f"{vote_button_type}:{option.id}:{result}"
        if poll.should_show_result() and poll.show_option_votes:
            text = i18n.t(
                "keyboard.vote_with_count",
                option_name=option_name,
                count=len(option.votes),
                locale=poll.locale,
            )
        else:
            text = option_name
        buttons.append([InlineKeyboardButton(text, callback_data=payload)])

    return buttons


def get_cumulative_buttons(poll: Poll) -> List[List[InlineKeyboardButton]]:
    """Get the cumulative keyboard with two buttons per option."""
    vote_button_type = CallbackType.vote.value
    vote_yes = CallbackResult.yes.value
    vote_no = CallbackResult.no.value

    options = poll.options

    buttons = []
    for option in options:
        option_name = option.get_formatted_name()

        yes_payload = f"{vote_button_type}:{option.id}:{vote_yes}"
        no_payload = f"{vote_button_type}:{option.id}:{vote_no}"
        buttons.append(
            [
                InlineKeyboardButton(f"－ {option_name}", callback_data=no_payload),
                InlineKeyboardButton(f"＋ {option_name}", callback_data=yes_payload),
            ]
        )

    return buttons


def get_priority_buttons(
    poll: Poll, user: Optional[User]
) -> List[List[InlineKeyboardButton]]:
    """Create the keyboard for priority poll. Only show the deeplink, if not in a direct conversation."""
    if user is None:
        bot_name = config["telegram"]["bot_name"]
        payload = get_start_button_payload(poll, StartAction.vote)
        url = f"http://t.me/{bot_name}?start={payload}"
        buttons = [
            [InlineKeyboardButton(i18n.t("keyboard.vote", locale=poll.locale), url=url)]
        ]

        return buttons

    buttons = []
    options = get_sorted_options(poll)
    vote_button_type = CallbackType.vote.value
    vote_increase = CallbackResult.increase_priority.value
    vote_decrease = CallbackResult.decrease_priority.value
    session = get_session()
    votes = (
        session.query(Vote)
        .filter(Vote.poll == poll)
        .filter(Vote.user == user)
        .order_by(Vote.priority.asc())
        .options(joinedload(Vote.option))
        .all()
    )

    indices = get_option_indices(options)
    for index, vote in enumerate(votes):
        option = vote.option
        if not poll.compact_buttons:
            name_row = [
                InlineKeyboardButton(f"{option.name}", callback_data=IGNORE_PAYLOAD)
            ]
            buttons.append(name_row)
        name_hint_payload = (
            f"{CallbackType.show_option_name.value}:{poll.id}:{option.id}"
        )
        increase_payload = f"{vote_button_type}:{option.id}:{vote_increase}"
        decrease_payload = f"{vote_button_type}:{option.id}:{vote_decrease}"
        ignore_payload = f"{CallbackType.ignore.value}:0:0"

        vote_row = []
        if poll.compact_buttons:
            vote_row.append(
                InlineKeyboardButton(
                    f"{indices[index]})", callback_data=name_hint_payload
                )
            )

        if index != len(votes) - 1:
            vote_row.append(InlineKeyboardButton("▼", callback_data=decrease_payload))
        else:
            vote_row.append(InlineKeyboardButton(" ", callback_data=ignore_payload))

        if index != 0:
            vote_row.append(InlineKeyboardButton("▲", callback_data=increase_payload))
        else:
            vote_row.append(InlineKeyboardButton(" ", callback_data=ignore_payload))

        buttons.append(vote_row)
    return buttons


def get_doodle_buttons(poll: Poll) -> List[List[InlineKeyboardButton]]:
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
        name_hint_payload = f"{show_option_name}:{poll.id}:{option.id}"
        yes_payload = f"{vote_button_type}:{option.id}:{vote_yes}"
        maybe_payload = f"{vote_button_type}:{option.id}:{vote_maybe}"
        no_payload = f"{vote_button_type}:{option.id}:{vote_no}"

        # If we don't have the compact button view, display the option name on it's own button row
        if not poll.compact_buttons:
            option_row = [
                InlineKeyboardButton(
                    option.get_formatted_name(), callback_data=name_hint_payload
                )
            ]
            buttons.append(option_row)
            option_row = []
        else:
            option_row = [
                InlineKeyboardButton(
                    f"{indices[index]})", callback_data=name_hint_payload
                )
            ]

        vote_row = [
            InlineKeyboardButton("✅", callback_data=yes_payload),
            InlineKeyboardButton("❔", callback_data=maybe_payload),
            InlineKeyboardButton("❌", callback_data=no_payload),
        ]

        buttons.append(option_row + vote_row)

    return buttons
