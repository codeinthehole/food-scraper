SHELL=/bin/bash

# Versions
PIP_VERSION=25.0

# Virtualenv

.PHONY: install
install: install_prerequisites requirements.txt
	uv pip sync requirements.txt <(echo "-e .")

.PHONY: install_prerequisites
install_prerequisites:
	uv pip install pip==$(PIP_VERSION)

requirements.txt: pyproject.toml
	uv pip compile pyproject.toml --output-file requirements.txt

.PHONY: upgrade
upgrade: install_prerequisites
	uv pip compile -U pyproject.toml --output-file requirements.txt

# Static analysis

.PHONY: check
check: ruff_format ruff_lint mypy test

.PHONY: mypy
mypy:
	mypy .

.PHONY: ruff_format
ruff_format:
	ruff format --check .

.PHONY: ruff_lint
ruff_lint:
	ruff check .

.PHONY: yamlfix
yamlfix:
	yamlfix --check .

# Testing

.PHONY: test
test:
	pytest -v tests/

# Smoke testing

.PHONY: run
run: update_prices update_charts update_overview update_timeline update_product_docs

.PHONY: update_prices
update_prices:
	@echo Updating /tmp/archive.json
	cp data/archive.json /tmp/archive.json
	chow update-price-archive data/products.json /tmp/archive.json

.PHONY: update_charts
update_charts:
	@echo Generating charts in /tmp/charts
	mkdir -p /tmp/charts
	chow generate-graphs data/archive.json /tmp/charts

.PHONY: update_overview
update_overview:
	@echo Generating overview in /tmp/overview.md
	chow generate-overview data/archive.json /tmp/charts /tmp/overview.md

.PHONY: update_timeline
update_timeline:
	@echo Generating timeline in /tmp/timeline.md
	chow generate-timeline data/archive.json /tmp/timeline.md

.PHONY: update_product_docs
update_product_docs:
	@echo Generating product docs in /tmp/product-docs
	mkdir -p /tmp/product-docs
	chow generate-product-documents data/archive.json /tmp/charts /tmp/
