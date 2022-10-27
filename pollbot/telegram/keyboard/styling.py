from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from pollbot.enums import CallbackType, OptionSorting, UserSorting
from pollbot.i18n import i18n
from pollbot.models.poll import Poll

from .settings import get_back_to_settings_button


def get_styling_settings_keyboard(poll: Poll) -> InlineKeyboardMarkup:
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

    # Decide whether votes should be summarized
    if poll.results_visible and not poll.is_priority():
        # We still show the button with a hint, in case the poll is permanently summarized.
        if poll.permanently_summarized:
            text = i18n.t("keyboard.styling.permanently_summarized", locale=locale)
            payload = f"{CallbackType.ignore.value}:0:0"
            buttons.append([InlineKeyboardButton(text=text, callback_data=payload)])

        else:
            if poll.summarize:
                text = i18n.t("keyboard.dont_summarize_votes", locale=locale)
            else:
                text = i18n.t("keyboard.summarize_votes", locale=locale)

            payload = f"{CallbackType.settings_toggle_summarization.value}:{poll.id}:0"
            buttons.append([InlineKeyboardButton(text=text, callback_data=payload)])

    # Date format styling between US and european
    if poll.has_date_option():
        text = (
            "📅 yyyy-mm-dd date format"
            if poll.european_date_format
            else "📅 dd.mm.yyyy date format"
        )
        payload = f"{CallbackType.settings_toggle_date_format.value}:{poll.id}:0"
        buttons.append([InlineKeyboardButton(text=text, callback_data=payload)])

    # Button to switch between compact vote button mode and verbose buttons
    # This is only used in doodle and priority polls
    if poll.is_doodle() or poll.is_priority():
        text = i18n.t("keyboard.compact_doodle", locale=locale)
        if poll.compact_buttons:
            text = i18n.t("keyboard.no_compact_doodle", locale=locale)
        payload = f"{CallbackType.settings_toggle_compact_buttons.value}:{poll.id}:0"
        buttons.append([InlineKeyboardButton(text=text, callback_data=payload)])

    # Add buttons for changing the sorting order of users
    if not poll.anonymous and not poll.is_doodle() and not poll.is_priority():
        for sorting in UserSorting:
            sorting_text = i18n.t(
                "keyboard.order_users",
                locale=locale,
                name=i18n.t(f"sorting.{sorting.name}", locale=locale),
            )

            if sorting.name == poll.user_sorting:
                sorting_text = "► " + sorting_text
            else:
                sorting_text = "▻ " + sorting_text

            button = InlineKeyboardButton(
                sorting_text,
                callback_data=f"{CallbackType.settings_user_sorting.value}:{poll.id}:{sorting.value}",
            )
            buttons.append([button])

    # Add buttons for changing the sorting order of options
    for sorting in OptionSorting:
        # If the poll is a doodle or priority poll, only manual sorting is allowed.
        # We can thereby simply not display the option to switch the sorting mode.
        if poll.is_doodle() or poll.is_priority():
            break

        sorting_text = i18n.t(
            "keyboard.order_options",
            locale=locale,
            name=i18n.t(f"sorting.{sorting.name}", locale=locale),
        )

        if sorting.name == poll.option_sorting:
            sorting_text = "► " + sorting_text
        else:
            sorting_text = "▻ " + sorting_text

        button = InlineKeyboardButton(
            sorting_text,
            callback_data=f"{CallbackType.settings_option_sorting.value}:{poll.id}:{sorting.value}",
        )
        buttons.append([button])

    if OptionSorting.manual.name == poll.option_sorting:
        # Button for manually adjusting the order of poll options
        button = InlineKeyboardButton(
            i18n.t("keyboard.order_options_manually", locale=locale),
            callback_data=f"{CallbackType.settings_open_option_order_menu.value}:{poll.id}:0",
        )
        buttons.append([button])

    buttons.append([get_back_to_settings_button(poll)])

    return InlineKeyboardMarkup(buttons)


def get_manual_option_order_keyboard(poll: Poll) -> InlineKeyboardMarkup:
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
