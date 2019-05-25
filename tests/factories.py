"""Factories for creating new databse objects."""
from pollbot.models import User


def user_factory(session, user_id, name, admin=False):
    """Create a user."""
    user = User(user_id, name)
    session.add(user)
    session.commit()

    return user
