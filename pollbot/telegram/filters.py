from typing import cast

from telegram import Poll as NativePoll
from telegram.ext import MessageFilter


class _Quiz(MessageFilter):
    name = "Filters.quiz"

    def filter(self, message):
        return (
            bool(message.poll)
            and cast(NativePoll, message.poll).type == NativePoll.QUIZ
        )


class CustomFilters:
    quiz = _Quiz()
