from pollbot.telegram.keyboard.vote import get_vote_keyboard


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


