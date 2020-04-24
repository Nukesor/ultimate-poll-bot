from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from pollbot.i18n import i18n, supported_languages

from pollbot.helper.enums import (
    CallbackType,
    UserSorting,
    OptionSorting,
)

from .settings import get_back_to_settings_button


def get_styling_settings_keyboard(poll):
    """Get a keyboard for sorting options."""
    buttons = []
    locale = poll.user.locale

    if poll.results_visible and not poll.is_priority():
        # Show/hide percentage
        percentage_text = i18n.t("keyboard.show_percentage", locale=locale)
        if poll.show_percentage:
            percentage_text = i18n.t("keyboard.hide_percentage", locale=locale)
        percentage_payload = (
            f"{CallbackType.settings_toggle_percentage.value}:{poll.id}:0"
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=percentage_text, callback_data=percentage_payload
                )
            ]
        )

        # Show/hide option votes
        option_votes_text = i18n.t("keyboard.show_option_votes", locale=locale)
        if poll.show_option_votes:
            option_votes_text = i18n.t("keyboard.hide_option_votes", locale=locale)
        option_votes_payload = (
            f"{CallbackType.settings_toggle_option_votes.value}:{poll.id}:0"
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=option_votes_text, callback_data=option_votes_payload
                )
            ]
        )

    # Summarize votes in poll
    if (
        poll.results_visible
        and not poll.permanently_summarized
        and not poll.is_priority()
    ):
        summarize_text = i18n.t("keyboard.summarize_votes", locale=locale)
        if poll.summarize:
            summarize_text = i18n.t("keyboard.dont_summarize_votes", locale=locale)
        summarize_payload = (
            f"{CallbackType.settings_toggle_summarization.value}:{poll.id}:0"
        )
        buttons.append(
            [InlineKeyboardButton(text=summarize_text, callback_data=summarize_payload)]
        )

    # Date format styling between US and european
    if poll.has_date_option():
        date_format_text = (
            "📅 yyyy-mm-dd date format"
            if poll.european_date_format
            else "📅 dd.mm.yyyy date format"
        )
        date_format_payload = (
            f"{CallbackType.settings_toggle_date_format.value}:{poll.id}:0"
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=date_format_text, callback_data=date_format_payload
                )
            ]
        )

    if poll.is_doodle() or poll.is_priority():
        doodle_button_text = i18n.t("keyboard.compact_doodle", locale=locale)
        if poll.compact_buttons:
            doodle_button_text = i18n.t("keyboard.no_compact_doodle", locale=locale)
        doodle_button_payload = (
            f"{CallbackType.settings_toggle_compact_buttons.value}:{poll.id}:0"
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=doodle_button_text, callback_data=doodle_button_payload
                )
            ]
        )

    # Compile the possible options for user sorting
    if not poll.anonymous and not poll.is_doodle() and not poll.is_priority():
        for order in UserSorting:
            if order.name == poll.user_sorting:
                continue

            option_name = i18n.t(f"sorting.{order.name}", locale=locale)
            button = InlineKeyboardButton(
                i18n.t("keyboard.order_users", locale=locale, name=option_name),
                callback_data=f"{CallbackType.settings_user_sorting.value}:{poll.id}:{order.value}",
            )
            buttons.append([button])

    if poll.option_sorting == OptionSorting.manual.name:
        # Show percentage voting, if we are on manual and the poll is no doodle/priority vote
        if not (poll.is_doodle() or poll.is_priority()):
            order = OptionSorting.percentage
            sorting_translation = i18n.t(f"sorting.{order.name}", locale=locale)
            button = InlineKeyboardButton(
                i18n.t(
                    "keyboard.order_options", locale=locale, name=sorting_translation
                ),
                callback_data=f"{CallbackType.settings_option_sorting.value}:{poll.id}:{order.value}",
            )
            buttons.append([button])

        # Button for opening the menu used to manually adjust the option order
        order = OptionSorting.percentage
        sorting_translation = i18n.t(f"sorting.{order.name}", locale=locale)
        button = InlineKeyboardButton(
            i18n.t("keyboard.order_options_manually", locale=locale),
            callback_data=f"{CallbackType.settings_open_option_order_menu.value}:{poll.id}:0",
        )
        buttons.append([button])

    else:
        order = OptionSorting.manual
        sorting_translation = i18n.t(f"sorting.{order.name}", locale=locale)
        button = InlineKeyboardButton(
            i18n.t("keyboard.order_options", locale=locale, name=sorting_translation),
            callback_data=f"{CallbackType.settings_option_sorting.value}:{poll.id}:{order.value}",
        )
        buttons.append([button])

    buttons.append([get_back_to_settings_button(poll)])

    return InlineKeyboardMarkup(buttons)


def get_manual_option_order_keyboard(poll):
    """A keyboard which can be used to manually adjust the order of options in polls"""
    buttons = []

    for index, option in enumerate(poll.options):
        # Get back to the styling sub menu
        styling_payload = f"{CallbackType.settings_show_styling.value}:{poll.id}:0"
        buttons.append(
            [InlineKeyboardButton(text=option.name, callback_data=styling_payload)]
        )

        increase_type = CallbackType.settings_increase_option_index.value
        decrease_type = CallbackType.settings_decrease_option_index.value
        increase_payload = f"{increase_type}:{poll.id}:{option.id}"
        decrease_payload = f"{decrease_type}:{poll.id}:{option.id}"
        ignore_payload = f"{CallbackType.ignore.value}:0:0"

        row = []
        if index != len(poll.options) - 1:
            row.append(InlineKeyboardButton("▼", callback_data=increase_payload))
        else:
            row.append(InlineKeyboardButton(" ", callback_data=ignore_payload))

        if index != 0:
            row.append(InlineKeyboardButton("▲", callback_data=decrease_payload))
        else:
            row.append(InlineKeyboardButton(" ", callback_data=ignore_payload))

        buttons.append(row)

    # Get back to the styling sub menu
    styling_text = i18n.t("keyboard.back", locale=poll.locale)
    styling_payload = f"{CallbackType.settings_show_styling.value}:{poll.id}:0"
    buttons.append(
        [InlineKeyboardButton(text=styling_text, callback_data=styling_payload)]
    )

    return InlineKeyboardMarkup(buttons)
