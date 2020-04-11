"""Helper class to get a database engine and to get a session."""
from pollbot.config import config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(
    config["database"]["sql_uri"],
    pool_size=config["database"]["connection_count"],
    max_overflow=config["database"]["overflow_count"],
    echo=False,
)
base = declarative_base(bind=engine)


def get_session(connection=None):
    """Get a new db session."""
    session = scoped_session(sessionmaker(bind=engine))
    return session
