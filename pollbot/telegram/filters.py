from typing import cast

from telegram import Poll as NativePoll
from telegram.ext import BaseFilter


class _Quiz(BaseFilter):
    name = "Filters.quiz"

    def filter(self, message):
        """
        Returns true if the message should be run.

        Args:
            self: (todo): write your description
            message: (str): write your description
        """
        return (
            bool(message.poll)
            and cast(NativePoll, message.poll).type == NativePoll.QUIZ
        )


class CustomFilters:
    quiz = _Quiz()
