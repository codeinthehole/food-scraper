# Virtualenv

install:
	pip install pip==22.3.1 pip-tools==6.8
	pip-sync

# Static analysis

check: black isort flake8 mypy test

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


# Smoke testing

run: update_prices update_charts update_overview update_timeline

update_prices:
	@echo Updating /tmp/prices.json
	cp prices.json /tmp/prices.json
	python main.py update-price-archive products.json /tmp/prices.json

update_charts:
	@echo Generating charts in /tmp/charts
	mkdir -p /tmp/charts
	python main.py generate-graphs prices.json /tmp/charts

update_overview:
	@echo Generating overview in /tmp/overview.md
	python main.py generate-overview prices.json /tmp/charts /tmp/overview.md

update_timeline:
	@echo Generating timeline in /tmp/timeline.md
	python main.py generate-timeline prices.json /tmp/timeline.md
