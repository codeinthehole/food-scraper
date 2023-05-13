# Virtualenv

install:
	pip install pip==23.1.2 pip-tools==6.13
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
	pytest -v tests/

# Smoke testing

run: update_prices update_charts update_overview update_timeline

update_prices:
	@echo Updating /tmp/archive.json
	cp data/archive.json /tmp/archive.json
	python main.py update-price-archive data/products.json /tmp/archive.json

update_charts:
	@echo Generating charts in /tmp/charts
	mkdir -p /tmp/charts
	python main.py generate-graphs data/archive.json /tmp/charts

update_overview:
	@echo Generating overview in /tmp/overview.md
	python main.py generate-overview data/archive.json /tmp/charts /tmp/overview.md

update_timeline:
	@echo Generating timeline in /tmp/timeline.md
	python main.py generate-timeline data/archive.json /tmp/timeline.md
