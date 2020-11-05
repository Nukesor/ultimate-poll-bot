from pollbot.i18n import i18n
from pollbot.config import config


def poll_required(function):
    """Return if the poll does not exist in the context object."""

    def wrapper(session, context):
        """
        Return a fresh session instance for the user.

        Args:
            session: (todo): write your description
            context: (dict): write your description
        """
        if context.poll is None or context.poll.delete is not None:
            return i18n.t("callback.poll_no_longer_exists", locale=context.user.locale)

        return function(session, context, context.poll)

    return wrapper


def admin_required(function):
    """Return if the poll does not exist in the context object."""

    def wrapper(bot, update, session, user):
        """
        Create a user.

        Args:
            bot: (todo): write your description
            update: (todo): write your description
            session: (todo): write your description
            user: (str): write your description
        """
        if user.username.lower() != config["telegram"]["admin"].lower():
            return i18n.t("admin.not_allowed", locale=user.locale)

        return function(bot, update, session, user)

    return wrapper
