import json
import os
from typing import TypedDict

import jsonschema


class PriceChange(TypedDict):
    date: str
    price: str


class ProductPriceHistory(TypedDict):
    name: str
    prices: list[PriceChange]


ArchiveProductMap = dict[str, ProductPriceHistory]


class InvalidJSON(Exception):
    pass


ARCHIVE_SCHEMA = {
    "type": "object",
    "patternProperties": {
        r"^\d+$": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                },
                "prices": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                            },
                            "price": {
                                "type": "string",
                            },
                        },
                        "required": ["date", "price"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["name", "prices"],
            "additionalProperties": False,
        }
    },
    "additionalProperties": False,
}


def load(filepath: str) -> ArchiveProductMap:
    """
    Return the product archive data structure.
    """
    # Archive is stored in a local file.
    if not os.path.exists(filepath):
        return {}

    # Decode file content.
    with open(filepath) as f:
        try:
            content: ArchiveProductMap = json.load(f)
        except json.decoder.JSONDecodeError as e:
            raise InvalidJSON("JSON could not be decoded") from e

    # Validate against schema.
    try:
        jsonschema.validate(instance=content, schema=ARCHIVE_SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        raise InvalidJSON("JSON does not conform to schema") from e

    return content


def save(filepath: str, archive: ArchiveProductMap) -> None:
    """
    Save the product archive data structure.
    """
    with open(filepath, "w") as f:
        json.dump(archive, f, indent=4)
