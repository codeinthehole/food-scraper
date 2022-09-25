# Ocado price scraper

A simple script for scraping prices of a list of products from Ocado.

## Local installation

Create a Python 3.10 virtualenv, then run::

    make install

which will install `pip-tools` and install the necessary packages.

Check formatting and type annotations with:

    make check

Run tests with

    make test

## Local running

Execute the price fetching script with:

    python main.py

which will update a local `prices.json` file.
