"""Text helper for poll creation."""
from pollbot.helper import translate_poll_type
from pollbot.i18n import i18n
from pollbot.helper.enums import ExpectedInput


def get_poll_type_help_text(poll):
    """Create the help text for vote types."""
    locale = poll.user.locale
    text = f"""{i18n.t('creation.current_poll_type', locale=locale)}: *{translate_poll_type(poll.poll_type, locale)}*

*{i18n.t('poll_types.single_vote', locale=locale)}*:
{i18n.t('creation.help.single_help', locale=locale)}

*{i18n.t('poll_types.doodle', locale=locale)}*:
{i18n.t('creation.help.doodle_help', locale=locale)}

*{i18n.t('poll_types.block_vote', locale=locale)}*:
{i18n.t('creation.help.block_help', locale=locale)}

*{i18n.t('poll_types.limited_vote', locale=locale)}*:
{i18n.t('creation.help.limited_help', locale=locale)}

*{i18n.t('poll_types.cumulative_vote', locale=locale)}*:
{i18n.t('creation.help.cumulative_help', locale=locale)}

{i18n.t('creation.help.unlimited_votes', locale=locale)}:
{i18n.t('creation.help.unlimited_help', locale=locale)}
"""
    return text


def get_init_text(poll):
    """Compile the poll creation initialization text."""
    locale = poll.user.locale
    poll.user.current_poll = poll
    poll.user.expected_input = ExpectedInput.name.name

    anonymity = i18n.t('creation.no_anonymity', locale=locale)
    if poll.anonymous:
        anonymity = i18n.t('creation.anonymity', locale=locale)

    results_visible = i18n.t('creation.results_not_visible', locale=locale)
    if poll.results_visible:
        results_visible = i18n.t('creation.results_visible', locale=locale)

    message = i18n.t(
        'creation.init_text',
        locale=poll.user.locale,
        poll_type=translate_poll_type(poll.poll_type, poll.locale),
        anonymity=anonymity,
        results_visible=results_visible,
    )
    return message


def get_datepicker_text(poll):
    """Get the text for the datepicker."""
    text = i18n.t('creation.datepicker_text', locale=poll.locale)
    for option in poll.options:
        text += f'\n{option.get_formatted_name()}'

    return text
