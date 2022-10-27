"""The settings management text."""
from pollbot.config import config
from pollbot.enums import PollType, StartAction
from pollbot.helper import get_escaped_bot_name
from pollbot.i18n import i18n
from pollbot.models.poll import Poll
from pollbot.models.user import User
from pollbot.poll.helper import translate_poll_type
from pollbot.telegram.keyboard.helper import get_start_button_payload


def get_settings_text(poll: Poll) -> str:
    """Compile the options text for this poll."""
    text = []
    locale = poll.user.locale
    text.append(
        i18n.t(
            "settings.poll_type",
            locale=locale,
            poll_type=translate_poll_type(poll.poll_type, locale),
        )
    )

    text.append(i18n.t("settings.language", locale=locale, language=poll.locale))

    if poll.anonymous:
        text.append(i18n.t("settings.anonymous", locale=locale))
    elif not poll.is_priority():
        text.append(i18n.t("settings.not_anonymous", locale=locale))

    if poll.results_visible:
        text.append(i18n.t("settings.results_visible", locale=locale))
    else:
        text.append(i18n.t("settings.results_not_visible", locale=locale))

    if poll.due_date:
        text.append(
            i18n.t(
                "settings.due_date", locale=locale, date=poll.get_formatted_due_date()
            )
        )
    else:
        text.append(i18n.t("settings.no_due_date", locale=locale))

    text.append("")

    text.append("*------- Styling -------*")
    text.append("")
    if poll.allow_new_options:
        text.append(i18n.t("settings.user_options", locale=locale))
    else:
        text.append(i18n.t("settings.no_user_options", locale=locale))

    if poll.results_visible:
        if poll.show_percentage:
            text.append(i18n.t("settings.percentage", locale=locale))
        else:
            text.append(i18n.t("settings.no_percentage", locale=locale))

        if poll.permanently_summarized:
            text.append(i18n.t("settings.permanently_summarized", locale=locale))
        elif poll.summarize:
            text.append(i18n.t("settings.summarize", locale=locale))
        else:
            text.append(i18n.t("settings.dont_summarize", locale=locale))

    if poll.has_date_option():
        if poll.european_date_format:
            text.append(i18n.t("settings.euro_date_format", locale=locale))
        else:
            text.append(i18n.t("settings.us_date_format", locale=locale))

    text.append("")

    # Sorting of user names
    if poll.poll_type == PollType.doodle.name:
        sorting_name = i18n.t("sorting.doodle", locale=locale)
        text.append(i18n.t("settings.user_sorting", locale=locale, name=sorting_name))
    elif not poll.anonymous:
        sorting_name = i18n.t(f"sorting.{poll.user_sorting}", locale=locale)
        text.append(i18n.t("settings.user_sorting", locale=locale, name=sorting_name))

    sorting_name = i18n.t(f"sorting.{poll.option_sorting}", locale=locale)
    text.append(i18n.t("settings.option_sorting", locale=locale, name=sorting_name))

    bot_name = get_escaped_bot_name()
    if poll.allow_sharing:
        text.append("")
        text.append(i18n.t("settings.sharing_link", locale=locale, name=sorting_name))

        payload = get_start_button_payload(poll, StartAction.share_poll)
        text.append(f"https://t.me/{bot_name}?start={payload}")

    if config["telegram"]["allow_private_vote"]:
        text.append("")
        text.append(i18n.t("settings.private_vote_link", locale=locale))
        payload = get_start_button_payload(poll, StartAction.vote)
        text.append(f"https://t.me/{bot_name}?start={payload}")

    if config["telegram"]["allow_private_vote"] or poll.allow_sharing:
        text.append("")
        text.append(i18n.t("settings.link_warning", locale=locale))

    return "\n".join(text)


def get_user_settings_text(user: User) -> str:
    """Get information about the user."""
    locale = user.locale

    text = ["*Current settings:*\n"]

    text.append(i18n.t("settings.user.language", locale=locale, language=user.locale))
    text.append(i18n.t("settings.user.explanations.language", locale=locale))
    text.append("")

    if user.notifications_enabled:
        text.append(i18n.t("settings.user.notifications_enabled", locale=locale))
    else:
        text.append(i18n.t("settings.user.notifications_disabled", locale=locale))
    text.append(i18n.t("settings.user.explanations.notifications", locale=locale))
    text.append("")

    def is_open(poll: Poll) -> bool:
        return not poll.closed and poll.created and poll.delete is None

    count = len(list(filter(is_open, user.polls)))

    def is_closed(poll: Poll) -> bool:
        return poll.closed and poll.delete is None

    text.append(i18n.t("settings.user.open_polls", locale=locale, count=count))
    count = len(list(filter(is_closed, user.polls)))
    text.append(i18n.t("settings.user.closed_polls", locale=locale, count=count))

    return "\n".join(text)
