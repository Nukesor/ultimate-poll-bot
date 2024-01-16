default: run

run:
    poetry run python main.py run

initdb *args:
    poetry run python main.py initdb {{ args }}
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
    poetry run ruff check ./pollbot --show-source
    poetry run ruff format ./pollbot --diff

format:
    poetry run ruff check --fix ./pollbot
    poetry run ruff format ./pollbot

# Watch for something
# E.g. `just watch lint` or `just watch test`
watch *args:
    watchexec --clear 'just {{ args }}'
