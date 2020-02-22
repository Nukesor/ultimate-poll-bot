from pollbot.i18n import i18n
from pollbot.telegram.keyboard.vote import get_vote_keyboard
from pollbot.display.poll import Context

from .option import get_option_information
from .vote import (
    get_vote_information_line,
    get_remaining_votes_lines,
)


def get_poll_text_and_vote_keyboard(
    session,
    poll,
    user=None,
    show_warning=False,
    show_back=False,
    inline_query=False
):
    """Get the text and the vote keyboard."""
    text, summarize = get_poll_text_and_summarize(
        session, poll,
        show_warning=False,
        inline_query=inline_query
    )

    keyboard = get_vote_keyboard(poll, user, show_back, summary=summarize)

    return text, keyboard


def get_poll_text(session, poll, show_warning=False):
    """Only get the poll text."""
    text, summarize = get_poll_text_and_summarize(session, poll, show_warning=False)
    return text


def get_poll_text_and_summarize(session, poll, show_warning=False, inline_query=False):
    """Get the poll text and vote keyboard."""
    summarize = poll.permanently_summarized or poll.summarize

    if not summarize:
        lines = compile_poll_text(session, poll,
                                  show_warning=show_warning,
                                  inline_query=inline_query)
        text = '\n'.join(lines)
        summarize = len(text) > 4000
        poll.permanently_summarized = summarize

    if summarize:
        lines = compile_poll_text(session, poll,
                                  show_warning=show_warning,
                                  summarize=summarize,
                                  inline_query=inline_query)
        text = '\n'.join(lines)

    if len(text) > 4000:
        text = i18n.t('misc.too_long', locale=poll.locale)

    return text, summarize


def compile_poll_text(session, poll, show_warning=False, summarize=False, inline_query=False):
    """Create the text of the poll."""
    context = Context(session, poll)

    # Name and description
    lines = []
    lines.append(f'✉️ **{poll.name}**')

    # Only send the name nad description, when using an inline_query
    # Otherwise the result may be too larg (due to many large poll texts)
    # and the inline query fails
    if inline_query:
        lines.append(i18n.t('poll.please_wait',
                            locale=poll.locale))
        return lines

    if poll.description is not None:
        lines.append(f'__{poll.description}__')

    # Anonymity information
    if not context.show_results or context.anonymous:
        lines.append('')
    if context.anonymous:
        lines.append(f"__{i18n.t('poll.anonymous', locale=poll.locale)}__")
        if context.show_results:
            lines.append(i18n.t('poll.anonymous_warning', locale=poll.locale))
    if not context.show_results:
        lines.append(f"__{i18n.t('poll.results_not_visible', locale=poll.locale)}__")

    lines += get_option_information(session, poll, context, summarize)
    lines.append('')

    if context.limited_votes:
        lines.append(i18n.t('poll.vote_times',
                            locale=poll.locale,
                            amount=poll.number_of_votes))

    # Total user count information
    information_line = get_vote_information_line(poll, context)
    if information_line is not None:
        lines.append(information_line)

    if context.show_results and not context.anonymous and \
            context.limited_votes and not summarize:
        remaining_votes = get_remaining_votes_lines(session, poll)
        lines += remaining_votes

    if poll.due_date is not None:
        lines.append(i18n.t('poll.due',
                            locale=poll.locale,
                            date=poll.get_formatted_due_date()))

    if not poll.closed and poll.compact_buttons:
        lines.append('')
        lines.append(i18n.t('poll.doodle_help', locale=poll.locale))
        lines.append('')

    # Own poll note
    lines.append(i18n.t('poll.own_poll', locale=poll.locale))

    # Notify users that poll is closed
    if poll.closed:
        lines.append(i18n.t('poll.closed', locale=poll.locale))

    if show_warning:
        lines.append(i18n.t('poll.too_many_votes', locale=poll.locale))

    return lines
