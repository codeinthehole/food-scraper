# Ocado price scraper

A Git-scraper repo for scraping prices from Ocado.

Once a day, the prices for a list of products (declared in
[`products.json`][products_file]) are fetched from Ocado and any changes are
recorded in [`prices.json`][prices_file]. Next, graphs of each product's prices
are generated (in the [`charts/` folder][charts_folder]) and an [overview
page][overview_file] is updated. Any changes are committed to the repo.

[products_file]:
  https://github.com/codeinthehole/food-scraper/blob/master/products.json
[prices_file]:
  https://github.com/codeinthehole/food-scraper/blob/master/prices.json
[charts_folder]:
  https://github.com/codeinthehole/food-scraper/blob/master/charts/
[overview_file]:
  https://github.com/codeinthehole/food-scraper/blob/master/overview.md

To browse historic price changes, [look for commits][commits_list] with subject
"Update price archive".

[commits_list]: https://github.com/codeinthehole/food-scraper/commits/master

## Local development

<details><summary><h3>Installation</h3></summary>

Create a Python 3.10 virtualenv, then run::

    make install

which will install `pip-tools` and the necessary packages.

</details>
<details><summary><h3>Running the application</h3></summary>

<details><summary><h4>Fetching new prices</h4></summary>

Update the price archive with:

    python main.py update-price-archive $PRODUCTS_FILE $ARCHIVE_FILE

which will take the products from `$PRODUCTS_FILE` and update `$ARCHIVE_FILE`
with the latest prices (if they have changed).

When run in Github's scheduler, the products file is `products.json` and the
archive file is `prices.json`.

</details>

<details><summary><h4>Product price charts</h4></summary>

Builds new versions of the product price charts with:

    python main.py generate-graphs $ARCHIVE_FILE $CHARTS_FOLDER

which will generate PNG chart images in `$CHARTS_FOLDER` based on the products
in `$ARCHIVE_FILE`.

</details>

<details><summary><h4>Smoke test</h4></summary>

To smoke test the application, run:

    make run

This will:

- Fetch product prices using `products.json` for the product list and update a
  throw-away copy of `prices.json`.

- Build product chart images in `/tmp/charts` based on the products in
  `prices.json`.

This shouldn't modify a file tracked in Git.

</details>

</details>
<details><summary><h3>Development</h3></summary>

Conventions:

- Code must be formatted with `black` and `isort`.
- Code must pass validation with `flake8`.
- Code must have type annotations and pass validation with `mypy`.

Check formatting and type annotations with:

    make check

See the `makefile` for how to run the linters individually.

</details>

<details><summary><h3>Python packages</h3></summary>

Packages are managed with [`pip-tools`](https://github.com/jazzband/pip-tools).
To add a new dependency, add it to `requirements.in` and run:

    pip-compile

which will generate a new version of `requirements.txt`. Then run:

    pip-sync

to install `requirements.txt`.

</details>

<details><summary><h3>Test suite</h3></summary>

#### Test suite structure

- `tests/unit/` contains isolated unit tests.
- `tests/integration/` contains tests that exercise a real external API.
- `tests/functional/` contains end-to-end tests that use Click's API to call
  commands.

#### Running tests

Run the CI tests with:

    make test

or the external tests with

    make integration_tests

</details>
