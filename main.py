import json
from typing import TextIO

import click

from chow import logger, usecases


@click.group()
def cli():
    pass


@cli.command()
@click.argument("products", type=click.File("rb"))
@click.argument("archive")
def update_price_archive(products: TextIO, archive: str) -> None:
    """
    Update a price archive JSON file with any prices changes and print a summary to STDOUT.
    """
    product_map: usecases.ProductMap = json.load(products)
    summary = usecases.update_price_archive(
        product_map=product_map,
        archive_filepath=archive,
        logger=logger.ConsoleLogger(debug_mode=True),
    )
    if summary:
        print(summary)


@cli.command()
@click.argument("archive")
@click.argument("folder")
def generate_graphs(archive: str, folder: str) -> None:
    """
    Update the product graphs.
    """
    usecases.generate_product_graphs(
        archive_filepath=archive,
        chart_folder=folder,
        logger=logger.ConsoleLogger(debug_mode=True),
    )


if __name__ == "__main__":
    cli()
