#!/bin/env python
"""Create a new database with schema."""
from contextlib import contextmanager

import typer
from sqlalchemy_utils.functions import database_exists, create_database, drop_database

from pollbot.db import engine, base
from pollbot.models import *  # noqa


def initialize_database(exist_ok: bool = False, drop_existing: bool = False):
    db_url = engine.url
    typer.echo(f"Using database at {db_url}")

    if database_exists(db_url):
        if drop_existing:
            with wrap_echo("Dropping database"):
                drop_database(db_url)
        elif not exist_ok:
            typer.echo(
                f"Database already exists, aborting.\n"
                f"Use --exist-ok if you are sure the database is uninitialized and contains no data.\n"
                f"Use --drop-existing if you want to recreate it.",
                err=True,
            )
            return

    with wrap_echo("Creating database"):
        create_database(db_url)
        pass

    with engine.connect() as con:
        with wrap_echo("Installing pgcrypto extension"):
            con.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
            pass

    with wrap_echo("Creating metadata"):
        base.metadata.create_all()
        pass

    typer.echo("Database initialization complete.")


@contextmanager
def wrap_echo(msg: str):
    typer.echo(f"{msg}... ", nl=False)
    yield
    typer.echo("done.")


if __name__ == "__main__":
    typer.run(initialize_database)
