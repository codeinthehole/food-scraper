import json
import pathlib
import sys
from typing import TextIO

import click
import jsonschema

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
    try:
        product_map = _load_products(products)
    except InvalidJSON as e:
        # Print out schema in case input it invalid.
        schema = json.dumps(PRODUCTS_SCHEMA, indent=4)
        click.secho(f"Error: {e}\nSchema:\n{schema}", fg="red")
        sys.exit(1)

    summary = usecases.update_price_archive(
        product_map=product_map,
        archive_filepath=archive,
        logger=logger.ConsoleLogger(debug_mode=True),
    )
    if summary:
        print(summary)


class InvalidJSON(Exception):
    pass


PRODUCTS_SCHEMA = {
    "type": "object",
    "patternProperties": {
        r"^\d+$": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                },
                "price": {
                    "type": "null",
                },
            },
            "required": ["name", "price"],
            "additionalProperties": False,
        }
    },
    "additionalProperties": False,
}


def _load_products(products: TextIO) -> usecases.ProductMap:
    """
    Load the product map from the passed text stream.

    Raises InvalidJSON if the JSON text is invalid.
    """
    # Decode JSON content.
    try:
        product_map: usecases.ProductMap = json.load(products)
    except json.decoder.JSONDecodeError as e:
        raise InvalidJSON("JSON could not be decoded") from e

    # Validate against schema.
    try:
        jsonschema.validate(instance=product_map, schema=PRODUCTS_SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        raise InvalidJSON("JSON does not conform to schema") from e

    return product_map


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


@cli.command()
@click.argument("archive")
@click.argument("folder")
@click.argument("overview_file")
def generate_overview(archive: str, folder: str, overview_file: str) -> None:
    """
    Generate a product overview in the passed file.
    """
    # Check archive file exists
    archive_filepath = pathlib.Path(archive)
    assert archive_filepath.is_file() and archive_filepath.exists()

    # Check charts folder exists
    charts_folder = pathlib.Path(folder)
    assert charts_folder.is_dir() and charts_folder.exists()

    # Overview doc doesn't necessarily exist.
    overview_filepath = pathlib.Path(overview_file)

    usecases.generate_overview_file(
        archive_filepath=archive_filepath,
        charts_folder=charts_folder,
        overview_filepath=overview_filepath,
        logger=logger.ConsoleLogger(debug_mode=True),
    )


@cli.command()
@click.argument("archive")
@click.argument("timeline_file")
def generate_timeline(archive: str, timeline_file: str) -> None:
    """
    Generate a timeline in the passed file.
    """
    # Check archive file exists
    archive_filepath = pathlib.Path(archive)
    assert archive_filepath.is_file() and archive_filepath.exists()

    # Timeline doc doesn't necessarily exist.
    timeline_filepath = pathlib.Path(timeline_file)

    usecases.generate_timeline_file(
        archive_filepath=archive_filepath,
        timeline_filepath=timeline_filepath,
        logger=logger.ConsoleLogger(debug_mode=True),
    )


if __name__ == "__main__":
    cli()
