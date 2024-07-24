# Ocado price scraper

A Git scraper repo for collecting prices from Ocado.

Contents:

- [What does this do?](#what-does-this-do?)
- [Local development](#local-development)
  - [Installation](#installation)
  - [Running the application](#running-the-application)
    - [Update price archive](#update-price-archive)
    - [Generate product detail documents](#generate-product-detail-documents)
    - [Generate timeline document](#generate-timeline-document)
    - [Generate product price charts](#generate-product-price-charts)
    - [Generate overview document](#generate-overview-document)
    - [Smoke test](#smoke-test)
  - [Application development](#application-development)
    - [Conventions](#conventions)
  - [Testing](#testing)
    - [Test suite structure](#test-suite-structure)
    - [Running tests](#running-tests)
  - [Packages](#packages)

## What does this do?

Once a day, the prices for a list of products (declared in
[`data/products.json`][products_file]) are fetched from Ocado and, if there are
any changes, they are recorded in [`data/archive.json`][prices_file].
Subsequently, product detail documents (of form `docs/product-$PRODUCT_ID.md`)
and a [`docs/timeline.md`][timeline_file] document are updated.

An hour later, graphs of each product's prices are generated (in the
[`docs/charts/` folder][charts_folder]) and an
[`docs/overview.md`][overview_file] file, which collates all the charts, is
updated.

Any changes are committed to the repo.

[products_file]: https://github.com/codeinthehole/food-scraper/blob/master/data/products.json
[prices_file]: https://github.com/codeinthehole/food-scraper/blob/master/data/archive.json
[timeline_file]: https://github.com/codeinthehole/food-scraper/blob/master/docs/timeline.md
[charts_folder]: https://github.com/codeinthehole/food-scraper/blob/master/docs/charts/
[overview_file]: https://github.com/codeinthehole/food-scraper/blob/master/docs/overview.md

To browse historic price changes, [look for commits][commits_list] with subject
"Update price archive".

[commits_list]: https://github.com/codeinthehole/food-scraper/commits/master

## Local development

### Installation

Create a Python 3.12 virtualenv. Ensure `uv` is installed as a system package
(e.g. installed with `pipx`). Then run::

    make install

which will install the necessary packages.

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

</details>

#### Generate product detail documents

Generate a new set of product detail documents with:

    python main.py generate-product-documents $ARCHIVE_FILE $CHARTS_FOLDER $DOCS_FOLDER

which will:

- Take the product data from `$ARCHIVE_FILE` and build a set of product detail
  documents in `$DOCS_FOLDER` using the corresponding charts from
  `$CHARTS_FOLDER`.

When [run as a Github action][gh_workflow_run], the archive file is
`data/archive.json`, the charts folder is `docs/charts/` and the docs folder is
`docs/`.

#### Generate timeline document

Generate a new timeline document with:

    python main.py generate-timeline $ARCHIVE_FILE $TIMELINE_FILE

which will:

- Take the product data from `$ARCHIVE_FILE` and build a timeline document in
  `$TIMELINE_FILE`.

When [run as a Github action][gh_workflow_run], the archive file is
`data/archive.json` and the timeline file is `docs/timeline.md`.

#### Generate product price charts

Build new versions of the product price charts with:

    python main.py generate-graphs $ARCHIVE_FILE $CHARTS_FOLDER

which will generate PNG chart images in `$CHARTS_FOLDER` based on the products
in `$ARCHIVE_FILE`.

When [run as a Github action][gh_workflow_charts], the archive file is
`data/archive.json` and the charts folder is `docs/charts/`.

#### Generate overview document

Build a Markdown overview document, that contains all product price graphs,
with:

    python main.py generate-overview $ARCHIVE_FILE $CHARTS_FOLDER $OVERVIEW_FILE

which will collate the product price charts for the products in `$ARCHIVE_FILE`
and store the overview document in `$OVERVIEW_FILE`.

When [run as a Github action][gh_workflow_charts], the archive file is
`data/archive.json`, the charts folder is `docs/charts/` and the overview
document is `docs/overview.md`.

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

### Application development

#### Conventions

Conventions:

- Code must be formatted with `ruff format`
- Code must pass validation with `ruff check`.
- Code must have type annotations and pass validation with `mypy`.

Check formatting and type annotations with:

    make check

See the `makefile` for how to run the linters individually.

### Testing

#### Test suite structure

- `tests/unit/` contains isolated unit tests.
- `tests/integration/` contains tests that exercise a real external API. These
  are skipped by default.
- `tests/functional/` contains end-to-end tests that use Click's API to call
  commands.

#### Running tests

Run the CI tests with:

    make test

### Packages

Packages are managed with [`uv`].

[`uv`]: https://github.com/astral-sh/uv

To add a new dependency, add it to `pyproject.toml` and run:

    make install

which will generate a new version of `requirements.txt` and install it.

To upgrade all dependencies inline with the constraints in `pyproject.toml`, run:

    make upgrade
    make install

To upgrade a single dependency, run:

    uv pip compile -P $package==$version --output-file requirements.txt pyproject.toml

to update `requirements.txt`, then:

    make install

to install the upgraded package.

[gh_workflow_run]: https://github.com/codeinthehole/food-scraper/blob/master/.github/workflows/run.yml
[gh_workflow_charts]: https://github.com/codeinthehole/food-scraper/blob/master/.github/workflows/charts.yml
