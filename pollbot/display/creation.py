"""Text helper for poll creation."""
from pollbot.helper import translate_poll_type
from pollbot.i18n import i18n
from pollbot.helper.enums import ExpectedInput


def get_poll_type_help_text(poll):
    """Create the help text for vote types."""
    locale = poll.user.locale

    message = i18n.t(
        'creation.poll_type_help',
        locale=locale,
        poll_type=translate_poll_type(poll.poll_type, locale),
    )

    return message


def get_init_text(poll):
    """Compile the poll creation initialization text."""
    locale = poll.user.locale
    poll.user.current_poll = poll
    poll.user.expected_input = ExpectedInput.name.name

    anonymity = i18n.t('creation.no_anonymity', locale=locale)
    if poll.anonymous:
        anonymity = i18n.t('creation.anonymity', locale=locale)

    anonymity_explanation = i18n.t('settings.poll.explanation.anonymity', locale=locale)

    results_visible = i18n.t('creation.results_not_visible', locale=locale)
    if poll.results_visible:
        results_visible = i18n.t('creation.results_visible', locale=locale)

    visibility_explanation = i18n.t('settings.poll.explanation.visibility', locale=locale)

    message = i18n.t(
        'creation.init_text',
        locale=poll.user.locale,
        poll_type=translate_poll_type(poll.poll_type, poll.locale),
        anonymity=anonymity,
        results_visible=results_visible,
        anonymityExplanation=anonymity_explanation,
        visibilityExplanation=visibility_explanation,
    )
    return message


def get_datepicker_text(poll):
    """Get the text for the datepicker."""
    text = i18n.t('creation.datepicker_text', locale=poll.locale)
    for option in poll.options:
        text += f'\n{option.get_formatted_name()}'

    return text
