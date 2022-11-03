# Ocado price scraper

A Git-scraper repo for scraping prices from Ocado.

Once a day, the `main.py` Python script is run via a Github Actions workflow.
This fetches prices for a list of products ([`products.json`][products_file])
and, if there are changes, updates the [`prices.json`][prices_file] file and
commits the change to the repo.

[products_file]:
  https://github.com/codeinthehole/food-scraper/blob/master/products.json
[prices_file]:
  https://github.com/codeinthehole/food-scraper/blob/master/prices.json

To browse historic price changes, [look for commits][commits_list] with subject
"Update price archive".

[commits_list]: https://github.com/codeinthehole/food-scraper/commits/master

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

    python main.py update-price-archive products.json prices.json

which will take the products from `products.json` and update `prices.json` with
the latest prices (if they have changed).

## Test suite

### Test suite structure

- `tests/unit/` contains isolated unit tests.
- `tests/integration/` contains tests that exercise a real external API.
- `tests/functional/` contains end-to-end tests that use Click's API to call
  commands.

### Running tests

Run the CI tests with:

    make test

or the external tests with

    make integration_tests
