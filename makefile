# Virtualenv

install:
	pip install pip-tools==6.8
	pip-sync

# Static analysis

check: black isort flake8 mypy unit_tests

mypy:
	mypy .

black:
	black --check .

isort:
	isort --check .

flake8:
	flake8

# Testing

test:
	pytest -v tests/unit/ tests/functional/

# These aren't run in CI as they hit external APIs.
integration_tests:
	pytest -v tests/integration/

run:
	@echo Updating /tmp/prices.json
	cp prices.json /tmp/prices.json
	python main.py update-price-archive products.json /tmp/prices.json
