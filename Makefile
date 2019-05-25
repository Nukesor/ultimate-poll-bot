.PHONY: default
default: run

.PHONY: install
install:
	poetry install --develop .

.PHONY: run
run:
	poetry run python main.py

.PHONY: test
test:
	poetry run pytest
