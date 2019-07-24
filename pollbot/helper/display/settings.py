"""The settings management text."""
from pollbot.i18n import i18n
from pollbot.helper import translate_poll_type
from pollbot.helper.enums import PollType


def get_settings_text(poll):
    """Compile the options text for this poll."""
    text = []
    locale = poll.user.locale
    text.append(i18n.t('settings.poll_type',
                       locale=locale,
                       poll_type=translate_poll_type(poll.poll_type, poll.locale)))

    text.append(i18n.t('settings.language', locale=locale, language=poll.locale))

    if poll.anonymous:
        text.append(i18n.t('settings.anonymous', locale=locale))
    else:
        text.append(i18n.t('settings.not_anonymous', locale=locale))

    if poll.due_date:
        text.append(i18n.t('settings.due_date', locale=locale,
                           date=poll.get_formatted_due_date()))
    else:
        text.append(i18n.t('settings.no_due_date', locale=locale))

    if poll.results_visible:
        text.append(i18n.t('settings.results_visible', locale=locale))
    else:
        text.append(i18n.t('settings.results_not_visible', locale=locale))

    text.append('')

    if poll.allow_new_options:
        text.append(i18n.t('settings.user_options', locale=locale))
    else:
        text.append(i18n.t('settings.no_user_options', locale=locale))

    if poll.results_visible:
        if poll.show_percentage:
            text.append(i18n.t('settings.percentage', locale=locale))
        else:
            text.append(i18n.t('settings.no_percentage', locale=locale))

    if poll.has_date_option():
        if poll.european_date_format:
            text.append(i18n.t('settings.euro_date_format', locale=locale))
        else:
            text.append(i18n.t('settings.us_date_format', locale=locale))

    text.append('')

    # Sorting of user names
    if poll.poll_type == PollType.doodle.name:
        sorting_name = i18n.t(f'sorting.doodle_sorting', locale=locale)
        text.append(i18n.t('settings.user_sorting', locale=locale, name=sorting_name))
    elif not poll.anonymous:
        sorting_name = i18n.t(f'sorting.{poll.user_sorting}', locale=locale)
        text.append(i18n.t('settings.user_sorting', locale=locale, name=sorting_name))

    sorting_name = i18n.t(f'sorting.{poll.option_sorting}', locale=locale)
    text.append(i18n.t('settings.option_sorting', locale=locale, name=sorting_name))

    return '\n'.join(text)
