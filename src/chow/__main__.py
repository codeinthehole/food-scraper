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
    Private base CLI group.
    """


@cli.command()
@click.argument("products", type=click.File("rb"))
@click.argument("archive", type=click.Path(exists=False))
def update_price_archive(products: TextIO, archive: str) -> None:
    """
    Update a price archive JSON file with any prices changes and print a summary to STDOUT.
    """
    try:
        product_list = _load_products(products)
    except InvalidJSON as e:
        # Print out schema in case input is invalid.
        schema = json.dumps(PRODUCTS_SCHEMA, indent=4)
        click.secho(f"Error: {e}\nSchema:\n{schema}", fg="red")
        sys.exit(1)

    summary = usecases.update_price_archive(
        products=product_list,
        archive_filepath=archive,
        logger=logger.ConsoleLogger(debug_mode=True),
    )
    if summary:
        print(summary)


class InvalidJSON(Exception):
    """
    For when JSON is invalid.
    """


# See https://json-schema.org/understanding-json-schema/
PRODUCTS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "ocado_product_id": {"type": "string"},
        },
        "required": ["name", "ocado_product_id"],
        "additionalProperties": False,
    },
}


def _load_products(products_content: TextIO) -> usecases.Products:
    """
    Load the product map from the passed text stream.

    Raises InvalidJSON if the JSON text is invalid.
    """
    # Decode JSON content.
    try:
        products: usecases.Products = json.load(products_content)
    except json.decoder.JSONDecodeError as e:
        raise InvalidJSON("JSON could not be decoded") from e

    # Validate against schema.
    try:
        jsonschema.validate(instance=products, schema=PRODUCTS_SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        raise InvalidJSON("JSON does not conform to schema") from e

    return products


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
    "products_folder",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, path_type=pathlib.Path
    ),
)
def generate_product_documents(
    archive_filepath: pathlib.Path,
    charts_folder: pathlib.Path,
    products_folder: pathlib.Path,
) -> None:
    """
    Generate product detail documents in the passed folder.
    """
    usecases.generate_product_detail_documents(
        archive_filepath=archive_filepath,
        charts_folder=charts_folder,
        products_folder=products_folder,
        logger=logger.ConsoleLogger(debug_mode=True),
    )


if __name__ == "__main__":
    cli()
