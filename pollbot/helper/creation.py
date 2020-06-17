"""Poll creation helper."""
from typing import List

from pollbot.display.poll.compilation import get_poll_text
from pollbot.helper.enums import ExpectedInput, ReferenceType
from pollbot.helper.exceptions import RollbackException
from pollbot.helper.stats import increase_stat, increase_user_stat
from pollbot.i18n import i18n
from pollbot.models import Option, Reference
from pollbot.telegram.keyboard import (
    get_options_entered_keyboard,
    get_management_keyboard,
)


def next_option(tg_chat, poll, options):
    """Send the options message during the creation ."""
    locale = poll.user.locale
    poll.user.expected_input = ExpectedInput.options.name
    keyboard = get_options_entered_keyboard(poll)

    if len(options) == 1:
        text = i18n.t("creation.option.single_added", locale=locale, option=options[0])
    else:
        text = i18n.t("creation.option.multiple_added", locale=locale)
        for option in options:
            text += f"\n*{option}*"
        text += "\n\n" + i18n.t("creation.option.next", locale=locale)

    if len(text) > 3800:
        error_message = i18n.t("misc.over_4000", locale=locale)
        raise RollbackException(error_message)

    tg_chat.send_message(text, reply_markup=keyboard, parse_mode="Markdown")


def create_poll(session, poll, user, chat, message=None):
    """Finish the poll creation."""
    poll.created = True
    user.expected_input = None
    user.current_poll = None

    text = get_poll_text(session, poll)

    if len(text) > 4000:
        error_message = i18n.t("misc.over_4000", locale=user.locale)
        message = chat.send_message(error_message, parse_mode="markdown")
        session.delete(poll)
        return

    if message:
        message = message.edit_text(
            text,
            parse_mode="markdown",
            reply_markup=get_management_keyboard(poll),
            disable_web_page_preview=True,
        )
    else:
        message = chat.send_message(
            text,
            parse_mode="markdown",
            reply_markup=get_management_keyboard(poll),
            disable_web_page_preview=True,
        )

    if len(text) > 3000:
        error_message = i18n.t("misc.over_3000", locale=user.locale)
        message = chat.send_message(error_message, parse_mode="markdown")

    reference = Reference(
        poll, ReferenceType.admin.name, user=user, message_id=message.message_id
    )
    session.add(reference)
    session.commit()

    increase_stat(session, "created_polls")
    increase_user_stat(session, user, "created_polls")


def add_text_options_from_list(session, poll, options: List[str]):
    """Add multiple new options to the poll."""
    options_to_add = map(str.strip, options)
    added_options = []

    for option_to_add in options_to_add:
        option = add_option(poll, option_to_add, added_options, False)
        if option is None:
            continue

        session.add(option)
        session.commit()

        added_options.append(option_to_add)

    return added_options


def add_options_multiline(session, poll, text, is_date=False):
    """Add one or multiple new options to the poll."""
    options_to_add = [x.strip() for x in text.split("\n") if x.strip() != ""]
    added_options = []

    for option_to_add in options_to_add:
        option = add_option(poll, option_to_add, added_options, is_date)
        if option is None:
            continue

        session.add(option)
        session.commit()

        added_options.append(option_to_add)

    return added_options


def add_option(poll, text, added_options, is_date):
    """Parse the incoming text and create a single option from it."""
    description = None
    description_descriminator = None
    if "--" in text:
        description_descriminator = "--"
    elif "—" in text:
        description_descriminator = "—"
    # Extract the description if existing

    if description_descriminator is not None:
        # Extract and strip the description
        splitted = text.split(description_descriminator, 1)
        text = splitted[0].strip()
        description = splitted[1].strip()
        if description == "":
            description = None

    if option_is_duplicate(poll, text) or text in added_options:
        return None

    option = Option(poll, text)
    option.description = description
    option.is_date = is_date
    poll.options.append(option)

    return option


def option_is_duplicate(poll, option_to_add):
    """Check whether this option already exists on this poll."""
    for existing_option in poll.options:
        if existing_option.name == option_to_add:
            return True

    return False
