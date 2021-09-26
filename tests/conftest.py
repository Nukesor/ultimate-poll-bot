"""Base fixtures for testing and import point for everything else."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import InternalError

from pollbot.db import base

from tests.fixtures import *  # noqa
from tests.helper import *  # noqa


@pytest.fixture(scope="session")
def engine():
    """Create the engine."""
    return create_engine("postgresql://localhost/pollbot_test")


@pytest.fixture(scope="session")
def tables(engine):
    """Create the base schema."""
    with engine.connect() as con:
        con.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        con.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    base.metadata.create_all(engine)
    yield
    base.metadata.drop_all(engine)


@pytest.fixture
def connection(engine, tables):
    """Create the connection for the test case."""
    connection = engine.connect()
    yield connection


@pytest.fixture
def session(connection, monkeypatch):
    """Return an sqlalchemy session, and after the test tear down everything properly."""
    # Begin the nested transaction
    transaction = connection.begin()
    # Use the connection with the already started transaction
    session = Session(bind=connection)

    def get_session():
        return session

    from pollbot import db

    monkeypatch.setattr(db, "get_session", get_session)
    assert session == db.get_session()

    yield session

    # Since we are not committing things to the database directly when
    # testing, initially deferred constraints are not checked. The
    # following statement makes the DB check these constraints. We are
    # executing this command AFTER the tests and NOT BEFORE, because
    # within a transaction the DB is allowed to take temporarily
    # invalid state. Read
    # https://www.postgresql.org/docs/current/static/sql-set-constraints.html
    # for details.
    try:
        connection.execute("SET CONSTRAINTS ALL IMMEDIATE")
    except InternalError:
        # This is the case when we are doing something in the tests
        # that we expect it to fail by executing the statement above.
        # In this case, the transaction will be in an already failed
        # state, executing further SQL statements are ignored and doing
        # so raises an exception.
        pass

    session.close()
    # Roll back the broader transaction
    transaction.rollback()
    # Put back the connection to the connection pool
    connection.close()
