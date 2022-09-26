# Virtualenv

install:
	pip install pip-tools==6.8
	pip-sync

# Static analysis

check: black isort flake8 mypy

mypy:
	mypy .

black:
	black --check .

isort:
	isort --check .

flake8:
	flake8

# Testing

test: unit_tests integration_tests

unit_tests:
	pytest -v tests/unit/

integration_tests:
	pytest -v tests/integration/
