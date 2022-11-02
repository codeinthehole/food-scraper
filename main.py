import json
from typing import TextIO

import click

from chow import usecases


@click.group()
def cli():
    pass


@cli.command()
@click.argument("products", type=click.File("rb"))
@click.argument("archive")
def update_price_archive(products: TextIO, archive: str) -> None:
    """
    Update a price archive JSON file.
    """
    product_map: usecases.ProductMap = json.load(products)
    summary = usecases.update_price_archive(
        product_map=product_map, archive_filepath=archive
    )
    if summary:
        print(summary)


if __name__ == "__main__":
    cli()
