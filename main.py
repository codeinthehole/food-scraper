import json
from typing import TextIO

import click

from chow import usecases


@click.group()
def cli():
    pass


@cli.command()
@click.argument("products_file", type=click.File("rb"))
def update_price_archive(products_file: TextIO) -> None:
    """
    Update a price archive JSON file.
    """
    products: usecases.ProductMap = json.load(products_file)
    summary = usecases.update_price_archive(products)
    if summary:
        print(summary)


if __name__ == "__main__":
    cli()
