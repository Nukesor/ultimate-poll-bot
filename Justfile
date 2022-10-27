default: run

run:
    poetry run python main.py run

initdb:
    poetry run python main.py initdb
    poetry run alembic --config migrations/alembic.ini stamp head

migrate:
    poetry run alembic --config migrations/alembic.ini upgrade head

setup:
    poetry install

test:
    #/bin/bash
    createdb pollbot_test || echo 'test database exists.'
    poetry run pytest

lint:
    poetry run black pollbot --check
    poetry run isort --check-only pollbot
    poetry run flake8 --exclude __init__.py,.venv,migrations

format:
    # remove unused imports
    poetry run autoflake \
        --remove-all-unused-imports \
        --recursive \
        --in-place pollbot \
        --exclude=__init__.py,.venv,migrations
    poetry run black pollbot
    poetry run isort pollbot


# Watch for something
# E.g. `just watch lint` or `just watch test`
watch *args:
    watchexec --clear 'just {{ args }}'
