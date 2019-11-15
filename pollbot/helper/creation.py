"""Poll creation helper."""
from pollbot.i18n import i18n
from pollbot.helper.stats import increase_stat
from pollbot.helper.enums import ExpectedInput
from pollbot.display.poll import get_poll_text
from pollbot.telegram.keyboard import (
    get_options_entered_keyboard,
    get_management_keyboard,
)
from pollbot.models import PollOption, Reference


def next_option(tg_chat, poll, options):
    """Send the options message during the creation ."""
    locale = poll.user.locale
    poll.user.expected_input = ExpectedInput.options.name
    keyboard = get_options_entered_keyboard(poll)

    if len(options) == 1:
        text = i18n.t('creation.option.single_added', locale=locale, option=options[0])
    else:
        text = i18n.t('creation.option.multiple_added', locale=locale)
        for option in options:
            text += f'\n*{option}*'
        text += '\n\n' + i18n.t('creation.option.next', locale=locale)

    tg_chat.send_message(text, reply_markup=keyboard, parse_mode='Markdown')


def create_poll(session, poll, user, chat, message=None):
    """Finish the poll creation."""
    poll.created = True
    user.expected_input = None
    user.current_poll = None

    text = get_poll_text(session, poll)

    if len(text) > 4000:
        error_message = i18n.t('misc.over_4000', locale=user.locale)
        message = chat.send_message(error_message, parse_mode='markdown')
        session.delete(poll)
        return

    if message:
        message = message.edit_text(
            text,
            parse_mode='markdown',
            reply_markup=get_management_keyboard(poll),
            disable_web_page_preview=True,
        )
    else:
        message = chat.send_message(
            text,
            parse_mode='markdown',
            reply_markup=get_management_keyboard(poll),
            disable_web_page_preview=True,
        )

    if len(text) > 3000:
        error_message = i18n.t('misc.over_3000', locale=user.locale)
        message = chat.send_message(error_message, parse_mode='markdown')

    reference = Reference(
        poll,
        admin_user=user,
        admin_message_id=message.message_id
    )
    session.add(reference)
    session.commit()

    increase_stat(session, 'created_polls')


def add_options(poll, text, is_date=False):
    """Add a new option to the poll."""
    options_to_add = [x.strip() for x in text.split('\n') if x.strip() != '']
    added_options = []

    for option_to_add in options_to_add:
        description = None
        # Extract the description if existing
        if not is_date and '-' in option_to_add:
            # Extract and strip the description
            splitted = option_to_add.split('-')
            option_to_add = splitted[0].strip()
            description = splitted[1].strip()
            if description == '':
                description = None

        if option_is_duplicate(poll, option_to_add) or option_to_add in added_options:
            continue

        poll_option = PollOption(poll, option_to_add)
        poll_option.description = description
        poll_option.is_date = is_date
        poll.options.append(poll_option)

        added_options.append(option_to_add)

    return added_options


def option_is_duplicate(poll, option_to_add):
    """Check whether this option already exists on this poll."""
    for existing_option in poll.options:
        if existing_option.name == option_to_add:
            return True

    return False
