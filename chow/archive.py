import json
import os
from typing import Dict, List, TypedDict


class PriceChange(TypedDict):
    date: str
    price: str


class ProductPriceHistory(TypedDict):
    name: str
    prices: List[PriceChange]


ArchiveProductMap = Dict[str, ProductPriceHistory]


def load(filepath: str) -> ArchiveProductMap:
    """
    Return the product archive data structure.
    """
    # Archive is stored in a local file.
    if not os.path.exists(filepath):
        return {}

    with open(filepath, "r") as f:
        return json.load(f)


def save(filepath: str, archive: ArchiveProductMap) -> None:
    """
    Save the product archive data structure.
    """
    with open(filepath, "w") as f:
        return json.dump(archive, f, indent=4)


def _filepath() -> str:
    """
    Return the filepath of the archive file.
    """
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "prices.json")
