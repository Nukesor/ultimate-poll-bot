"""Text helper for poll creation."""
from pollbot.enums import ExpectedInput
from pollbot.i18n import i18n
from pollbot.models import Poll
from pollbot.poll.helper import translate_poll_type


def get_poll_type_help_text(poll: Poll) -> str:
    """Create the help text for vote types."""
    locale = poll.user.locale

    message = i18n.t(
        "creation.poll_type_help",
        locale=locale,
        poll_type=translate_poll_type(poll.poll_type, locale),
    )

    return message


def get_init_text(poll: Poll) -> str:
    """Compile the poll creation initialization text."""
    locale = poll.user.locale
    poll.user.current_poll = poll
    poll.user.expected_input = ExpectedInput.name.name

    anonymity = i18n.t("creation.no_anonymity", locale=locale)
    if poll.anonymous:
        anonymity = i18n.t("creation.anonymity", locale=locale)

    results_visible = i18n.t("creation.results_not_visible", locale=locale)
    if poll.results_visible:
        results_visible = i18n.t("creation.results_visible", locale=locale)

    message = i18n.t(
        "creation.init_text",
        locale=poll.user.locale,
        poll_type=translate_poll_type(poll.poll_type, poll.locale),
        anonymity=anonymity,
        results_visible=results_visible,
    )
    return message


def get_init_anonymziation_settings_text(poll: Poll) -> str:
    locale = poll.locale
    text = ["*Poll Settings:*"]

    if poll.anonymous:
        text.append(f"*{i18n.t('creation.anonymity', locale=locale)}*")
    else:
        text.append(f"*{i18n.t('creation.no_anonymity', locale=locale)}*")

    text.append("")
    text.append(i18n.t("settings.poll.explanation.anonymity", locale=locale))
    text.append("")

    if poll.results_visible:
        text.append(f"*{i18n.t('creation.results_visible', locale=locale)}*")
    else:
        text.append(f"*{i18n.t('creation.results_not_visible', locale=locale)}*")

    text.append("")
    text.append(i18n.t("settings.poll.explanation.visibility", locale=locale))

    return "\n".join(text)


def get_datepicker_text(poll: Poll) -> str:
    """Get the text for the datepicker."""
    text = i18n.t("creation.datepicker_text", locale=poll.locale)
    for option in poll.options:
        text += f"\n{option.get_formatted_name()}"

    return text


def get_native_poll_merged_text(poll: Poll):
    locale = poll.locale

    anonymity = i18n.t("creation.no_anonymity", locale=locale)
    if poll.anonymous:
        anonymity = i18n.t("creation.anonymity", locale=locale)

    results_visible = i18n.t("creation.results_not_visible", locale=locale)
    if poll.results_visible:
        results_visible = i18n.t("creation.results_visible", locale=locale)

    message = i18n.t(
        "creation.native_poll.merged",
        locale=poll.user.locale,
        poll_type=translate_poll_type(poll.poll_type, poll.locale),
        anonymity=anonymity,
        results_visible=results_visible,
    )
    return message
