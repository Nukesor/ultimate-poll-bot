"""Helper enums to properly map several properties of Polls and alike."""
from enum import Enum, unique


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
class VoteType(Enum):
    """Helper class to specify the different types of Polls."""

    single_vote = 1
    block_vote = 2
    limited_vote = 3
    cumulative_vote = 4
    count_vote = 5


VoteTypeTranslation = {
    VoteType.single_vote.name: 'Single vote',
    VoteType.block_vote.name: 'Block vote',
    VoteType.limited_vote.name: 'Limited vote',
    VoteType.cumulative_vote.name: 'Cumulative vote',
    VoteType.count_vote.name: 'Unlimited votes',
}


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
    show_vote_type_keyboard = 0
    change_vote_type = 1
    toggle_anonymity = 2
    skip_description = 3
    all_options_entered = 4
    toggle_results_visible = 5
    cancel_creation = 6

    # Poll voting
    vote = 20

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
    close = 51
    reopen = 52
    clone = 53
    reset = 54

    # Settings
    settings_anonymization_confirmation = 70
    settings_anonymization = 71
    settings_show_sorting = 72
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

    # Misc
    ignore = 100

    # Date picker
    open_creation_datepicker = 501
    close_creation_datepicker = 502
    pick_date_option = 503
    set_date = 504
    next_month = 505
    previous_month = 506


@unique
class CallbackResult(Enum):
    """A class representing callback results."""

    empty = 0
    true = 1
    false = 2

    # Poll voting
    vote = 20
    vote_yes = 21
    vote_no = 22
    vote_maybe = 23

    # Menu navigation
    main_menu = 40
    settings = 41


@unique
class UserSorting(Enum):
    """Save several possible sorting options."""

    user_chrono = 0
    user_name = 1


@unique
class OptionSorting(Enum):
    """Save several possible sorting options."""

    option_chrono = 10
    option_percentage = 11
    option_name = 12


SortOptionTranslation = {
    UserSorting.user_chrono.name: 'chronologically',
    UserSorting.user_name.name: 'by name',
    OptionSorting.option_chrono.name: 'chronologically',
    OptionSorting.option_percentage.name: 'by percentage',
    OptionSorting.option_name.name: 'by name',
}
