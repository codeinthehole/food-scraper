# Ocado price scraper

A Git-scraper repo for scraping prices from Ocado.

Once a day, the `main.py` Python script is run via a Github Actions workflow.
This fetches prices for a list of products (`products.json`) and, if there are
changes, updates the `prices.json` file and commits the change to the repo.

To browse historic price changes, look for commits with subject "Update price
archive".

## Local development

### Installation

Create a Python 3.10 virtualenv, then run::

    make install

which will install `pip-tools` and the necessary packages.

### Development

Conventions:

- Code must be formatted with `black` and `isort`.
- Code must pass validation with `flake8`.
- Code must have type annotations and pass validation with `mypy`.

Check formatting and type annotations with:

    make check

See the `makefile` for how to run the linters individually.

### Running the application

Execute the price fetching script with:

    python main.py update-price-archive products.json

which will update a local `prices.json` file.

## Test suite

### Test suite structure

- `tests/unit/` contains isolated unit tests.
- `tests/integration/` contains tests that exercise a real external API.

### Running tests

Run all tests with:

    make test

or a category of test with:

    make unit_tests
    make integration_tests
