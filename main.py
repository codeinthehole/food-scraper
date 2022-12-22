import json
import pathlib
import sys
from typing import TextIO

import click
import jsonschema

from chow import logger, usecases


@click.group()
def cli() -> None:
    """
    Provate base CLI group.
    """


@cli.command()
@click.argument("products", type=click.File("rb"))
@click.argument("archive", type=click.Path(exists=False))
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
    """
    For when JSON is invalid.
    """


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
@click.argument(
    "archive",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path
    ),
)
@click.argument(
    "folder",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, path_type=pathlib.Path
    ),
)
def generate_graphs(archive: pathlib.Path, folder: pathlib.Path) -> None:
    """
    Update the product graphs.
    """
    usecases.generate_product_graphs(
        archive_filepath=archive,
        chart_folder=folder,
        logger=logger.ConsoleLogger(debug_mode=True),
    )


@cli.command()
@click.argument(
    "archive_filepath",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path
    ),
)
@click.argument(
    "charts_folder",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, path_type=pathlib.Path
    ),
)
@click.argument(
    "overview_filepath",
    type=click.Path(
        exists=False, file_okay=True, dir_okay=False, path_type=pathlib.Path
    ),
)
def generate_overview(
    archive_filepath: pathlib.Path,
    charts_folder: pathlib.Path,
    overview_filepath: pathlib.Path,
) -> None:
    """
    Generate a product overview in the passed file.
    """
    usecases.generate_overview_file(
        archive_filepath=archive_filepath,
        charts_folder=charts_folder,
        overview_filepath=overview_filepath,
        logger=logger.ConsoleLogger(debug_mode=True),
    )


@cli.command()
@click.argument(
    "archive_filepath",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, path_type=pathlib.Path
    ),
)
@click.argument(
    "timeline_filepath",
    type=click.Path(
        exists=False, file_okay=True, dir_okay=False, path_type=pathlib.Path
    ),
)
def generate_timeline(
    archive_filepath: pathlib.Path, timeline_filepath: pathlib.Path
) -> None:
    """
    Generate a timeline in the passed file.
    """
    usecases.generate_timeline_file(
        archive_filepath=archive_filepath,
        timeline_filepath=timeline_filepath,
        logger=logger.ConsoleLogger(debug_mode=True),
    )


if __name__ == "__main__":
    cli()
