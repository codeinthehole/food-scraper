# Ocado price scraper

A Git-scraper repo for scraping prices from Ocado.

Once a day, the prices for a list of products (declared in
[`data/products.json`][products_file]) are fetched from Ocado and any changes
are recorded in [`data/archive.json`][prices_file].

If there are any price changes, a [`timeline.md`][timeline_file] document is
updated.

Next, graphs of each product's prices are generated (in the [`charts/`
folder][charts_folder]) and an [`docs/overview.md`][overview_file] file is
updated. Any changes are committed to the repo.

[products_file]:
  https://github.com/codeinthehole/food-scraper/blob/master/data/products.json
[prices_file]:
  https://github.com/codeinthehole/food-scraper/blob/master/data/archive.json
[timeline_file]:
  https://github.com/codeinthehole/food-scraper/blob/master/timeline.md
[charts_folder]:
  https://github.com/codeinthehole/food-scraper/blob/master/charts/
[overview_file]:
  https://github.com/codeinthehole/food-scraper/blob/master/docs/overview.md

To browse historic price changes, [look for commits][commits_list] with subject
"Update price archive".

[commits_list]: https://github.com/codeinthehole/food-scraper/commits/master

## Local development

### Installation

Create a Python 3.10 virtualenv, then run::

    make install

which will install `pip-tools` and the necessary packages.

### Running the application

The application entry-point is `main.py` which uses [click][click_site] to
provide a series of subcommands. Run:

    python main.py

to see a list of available commands.

[click_site]: https://click.palletsprojects.com/en/8.1.x/

#### Update price archive

Update the price archive with:

    python main.py update-price-archive $PRODUCTS_FILE $ARCHIVE_FILE

which will:

- Take the products from `$PRODUCTS_FILE` and update `$ARCHIVE_FILE` with any
  new or updates prices.

- Print a summary of the changes to STDOUT.

When [run as a Github action][gh_workflow_run], the products file is
`data/products.json` and the archive file is `data/archive.json`.

[gh_workflow_run]:
  https://github.com/codeinthehole/food-scraper/blob/master/.github/workflows/run.yml

#### Generate product price charts

Build new versions of the product price charts with:

    python main.py generate-graphs $ARCHIVE_FILE $CHARTS_FOLDER

which will generate PNG chart images in `$CHARTS_FOLDER` based on the products
in `$ARCHIVE_FILE`.

When [run as a Github action][gh_workflow_charts], the archive file is
`data/archive.json` and the charts folder is `charts/`.

[gh_workflow_charts]:
  https://github.com/codeinthehole/food-scraper/blob/master/.github/workflows/charts.yml

#### Generate overview document

Build a Markdown overview document, that contains all product price graphs,
with:

    python main.py generate-overview $ARCHIVE_FILE $CHARTS_FOLDER $OVERVIEW_FILE

which will collate the product price charts for the products in `$ARCHIVE_FILE`
and store the overview document in `$OVERVIEW_FILE`.

When [run as a Github action][gh_workflow_charts], the archive file is
`data/archive.json`, the charts folder is `charts/` and the overview document is
`docs/overview.md`.

#### Smoke test

To informally check all the above commands are working, run:

    make run

This will:

- Fetch product prices using `data/products.json` for the product list and
  update a throw-away archive file in `/tmp/archive.json`.

- Build product chart images in `/tmp/charts` based on the products in
  `data/archive.json`.

- Build a throw-away overview document in `/tmp/overview.md`.

This shouldn't modify a file tracked in Git so can be run without dirtying your
local checkout.

### Development

Conventions:

- Code must be formatted with `black` and `isort`.
- Code must pass validation with `flake8`.
- Code must have type annotations and pass validation with `mypy`.

Check formatting and type annotations with:

    make check

See the `makefile` for how to run the linters individually.

### Test suite

### Test suite structure

- `tests/unit/` contains isolated unit tests.
- `tests/integration/` contains tests that exercise a real external API. These
  are skipped by default.
- `tests/functional/` contains end-to-end tests that use Click's API to call
  commands.

### Running tests

Run the CI tests with:

    make test

### Packages

Packages are managed with [`pip-tools`](https://github.com/jazzband/pip-tools).

To add a new dependency, add it to `requirements.in` and run:

    pip-compile requirements.in

which will generate a new version of `requirements.txt`. Then run:

    pip-sync

to install `requirements.txt`.

To upgrade a dependency, run:

    pip-compile -P $package==$version requirements.in

to update `requirements.txt`, then:

    pip-sync

to install the upgraded package.
