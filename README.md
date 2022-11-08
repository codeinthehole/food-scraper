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

### Running the application

#### Fetching new prices

Update the price archive with:

    python main.py update-price-archive $PRODUCTS_FILE $ARCHIVE_FILE

which will take the products from `$PRODUCTS_FILE` and update `$ARCHIVE_FILE`
with the latest prices (if they have changed).

When run in Github's scheduler, the products file is `products.json` and the
archive file is `prices.json`.

#### Product price charts

Builds new versions of the product price charts with:

    python main.py generate-graphs $ARCHIVE_FILE $CHARTS_FOLDER

which will generate PNG chart images in `$CHARTS_FOLDER` based on the products
in `$ARCHIVE_FILE`.

#### Smoke test

To smoke test the application, run:

    make run

This will:

- Fetch product prices using `products.json` for the product list and update a
  throw-away copy of `prices.json`.

- Build product chart images in `/tmp/charts` based on the products in
  `prices.json`.

This shouldn't modify a file tracked in Git.

### Development

Conventions:

- Code must be formatted with `black` and `isort`.
- Code must pass validation with `flake8`.
- Code must have type annotations and pass validation with `mypy`.

Check formatting and type annotations with:

    make check

See the `makefile` for how to run the linters individually.

### Packages

Packages are managed with [`pip-tools`](https://github.com/jazzband/pip-tools).
To add a new dependency, add it to `requirements.in` and run:

    pip-compile

which will generate a new version of `requirements.txt`. Then run:

    pip-sync

to install `requirements.txt`.

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
