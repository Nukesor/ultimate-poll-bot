"""Factories for creating new databse objects."""
from pollbot.models import User, Poll


def user_factory(session, user_id, name, admin=False):
    """Create a user."""
    user = User(user_id, name)
    session.add(user)
    session.commit()

    return user


def poll_factory(session, user):
    poll = Poll(user)
    session.add(poll)
    session.commit()

    return poll
