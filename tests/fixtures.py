"""Database test fixtures."""
import pytest
from tests.factories import user_factory, poll_factory


@pytest.fixture(scope="function")
def user(session):
    """Create a user."""
    return user_factory(session, 2, "TestUser")


@pytest.fixture(scope="function")
def poll(session, user):
    return poll_factory(session, user)
