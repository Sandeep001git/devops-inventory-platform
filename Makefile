.PHONY: test lint check

test:
	set -a; . ./.env.dev; set +a;\
 	POSTGRES_DB=devops_inventory_test    .venv/bin/python -m pytest -v

lint:
	.venv/bin/ruff check app tests

check: lint test
