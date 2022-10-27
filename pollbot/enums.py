"""Helper enums to properly map several properties of Polls and alike."""
from enum import Enum, unique


@unique
class PollDeletionMode(Enum):

    DB_ONLY = 1
    WITH_MESSAGES = 2


@unique
class ExpectedInput(Enum):
    """Helper class to map the creation steps of a Poll."""

    name = 1
    description = 2
    options = 3
    votes = 4
    vote_count = 5
    date = 6
    due_date = 7

    new_option = 10
    new_user_option = 11


@unique
class StartAction(Enum):
    """Helper enum to specify the different possible entry types for /start."""

    new_option = 0
    show_results = 1
    share_poll = 2
    vote = 3


@unique
class PollType(Enum):
    """Helper class to specify the different types of Polls."""

    single_vote = 0
    doodle = 10
    priority = 60
    count_vote = 50
    block_vote = 20
    limited_vote = 30
    cumulative_vote = 40


@unique
class ReferenceType(Enum):
    """Helper enum to specify the different types of possible votes."""

    inline = 1
    admin = 2
    private_vote = 3


@unique
class VoteResultType(Enum):
    """Helper enum to specify the different types of possible votes."""

    yes = 1
    no = 2
    maybe = 3


@unique
class CallbackType(Enum):
    """A class representing callback types."""

    # Poll creation
    show_poll_type_keyboard = 0
    change_poll_type = 1
    toggle_anonymity = 2
    skip_description = 3
    all_options_entered = 4
    toggle_results_visible = 5
    cancel_creation = 6
    back_to_init = 7
    anonymity_settings = 8
    cancel_creation_replace = 9
    ask_description = 10

    # Poll voting
    vote = 20
    update_shared = 21

    # Poll management menu
    menu_back = 30
    menu_vote = 31
    menu_option = 32
    menu_delete = 34
    menu_show = 35
    menu_update = 36
    menu_close = 37

    # Poll management
    delete = 50
    delete_poll_with_messages = 55
    close = 51
    reopen = 52
    clone = 53
    reset = 54

    # Settings
    settings_anonymization_confirmation = 70
    settings_anonymization = 71
    settings_show_styling = 72
    settings_user_sorting = 73
    settings_option_sorting = 74
    settings_new_option = 75
    settings_show_remove_option_menu = 76
    settings_remove_option = 77
    settings_toggle_percentage = 78
    settings_toggle_allow_new_options = 79
    settings_toggle_date_format = 80
    settings_open_add_option_datepicker = 81
    settings_open_due_date_datepicker = 82
    settings_pick_due_date = 83
    settings_open_language_picker = 84
    settings_change_poll_language = 85
    settings_toggle_summarization = 86
    settings_toggle_compact_buttons = 87
    settings_toggle_option_votes = 89
    settings_toggle_allow_sharing = 90
    settings_open_option_order_menu = 91
    settings_increase_option_index = 92
    settings_decrease_option_index = 93

    # Misc
    ignore = 100
    activate_notification = 101
    external_open_datepicker = 102
    external_open_menu = 103
    external_cancel = 104

    show_option_name = 110

    switch_help = 120

    # User
    user_menu = 200

    user_list_polls = 213
    user_list_polls_navigation = 218

    user_list_closed_polls = 215
    user_list_closed_polls_navigation = 220

    user_delete = 216
    user_delete_confirmation = 217

    # User Settings
    user_settings = 202
    user_language_menu = 203
    user_change_language = 204
    user_delete_all = 205
    user_delete_closed = 206
    user_delete_all_confirmation = 207
    user_delete_closed_confirmation = 208
    user_toggle_notification = 214

    # Admin Settings
    admin_settings = 209
    admin_plot = 211
    admin_update = 212

    # Misc
    open_help = 300
    donate = 301
    init_poll = 302

    # Datepicker
    open_creation_datepicker = 501
    close_creation_datepicker = 502
    next_month = 503
    previous_month = 504

    # Datepicker in creation menu
    pick_creation_date = 505
    pick_creation_weekday = 506

    # Datepicker for adding options by external users
    pick_external_date = 507

    # Datepicker in settings after poll creation
    pick_additional_date = 508
    pick_additional_weekday = 509

    # Datepicker for poll due date
    pick_due_date = 510


@unique
class CallbackResult(Enum):
    """A class representing callback results."""

    empty = 0
    true = 1
    false = 2

    # Poll voting
    vote = 20
    yes = 21
    no = 22
    maybe = 23
    increase_priority = 24
    decrease_priority = 25

    # Menu navigation
    main_menu = 40
    settings = 41


@unique
class UserSorting(Enum):
    """Save several possible sorting options."""

    chrono = 0
    name = 1


@unique
class OptionSorting(Enum):
    """Save several possible sorting options."""

    percentage = 11
    manual = 10


@unique
class DatepickerContext(Enum):
    """We reuse the datepicker in several places, this Enum lists the various context it's used in."""

    creation = 0
    additional_option = 1
    external_add_option = 2

    due_date = 10
