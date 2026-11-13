.PHONY: run migrate seed test lint

run:
	python manage.py runserver

migrate:
	python manage.py migrate

seed:
	python manage.py seed_demo

test:
	pytest

lint:
	ruff check .

