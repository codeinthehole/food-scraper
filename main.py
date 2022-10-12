import copy
import datetime
import json
import os
from typing import TypedDict

import bs4
import requests

# Data types


class RetailerPrice(TypedDict):
    # In format YYYY-MM-DD
    date: str
    # Price is in pence.
    price: int


class ProductRetailer(TypedDict):
    retailer: str
    product_id: str
    prices: list[RetailerPrice]


class Product(TypedDict):
    # Must be unique.
    code: str
    name: str
    retailers: list[ProductRetailer]


def main() -> None:
    """
    Update a price archive JSON file.
    """
    # Declare products to track.
    # TODO make this a separate file that is passed in.
    products: list[Product] = [
        {
            "code": "LURPAK_BUTTER_500G",
            "name": "Lurpak butter (500g)",
            "retailers": [
                {
                    "retailer": "Ocado",
                    "product_id": "13175011",
                    "prices": [],
                }
            ],
        },
        {
            "code": "NEW_YORK_BAGELS_5",
            "name": "New York bagels (5)",
            "retailers": [
                {
                    "retailer": "Ocado",
                    "product_id": "23476011",
                    "prices": [],
                }
            ],
        },
    ]

    # Append latest price to products dict.
    _fetch_product_prices(products)

    # Update archive file.
    current_archive = _load_archive()
    updated_archive = _update_price_archive(
        products=products,
        price_archive=current_archive,
    )

    # If the archive has changed, save it and print out a summary of changes.
    if updated_archive != current_archive:
        _save_archive(updated_archive)
        print(_change_summary(current_archive, updated_archive))


def _change_summary(current_archive, updated_archive) -> str:
    """
    Return a summary of the changes.
    """
    if current_archive == updated_archive:
        return ""

    # Build a list of changes.
    changes = []

    # Look for new products in updated archive.
    for product_id, product_data in updated_archive.items():
        if product_id not in current_archive:
            changes.append("New product: {name}".format(name=product_data["name"]))

    # Look for products with new prices (or removed) updated archive.
    for product_id, product_data in current_archive.items():
        if product_id not in updated_archive:
            changes.append("Remove product: {name}".format(name=product_data["name"]))
        else:
            updated_product_data = updated_archive[product_id]
            # Look for name change.
            if product_data["name"] != updated_product_data["name"]:
                changes.append(
                    "Rename product: {name} to {new_name}".format(
                        name=product_data["name"], new_name=updated_product_data["name"]
                    )
                )
            # Look for price change.
            if product_data["prices"] != updated_product_data["prices"]:
                previous_price = product_data["prices"][-1]["price"]
                new_price = updated_product_data["prices"][-1]["price"]
                changes.append(
                    "Price change for {name}: {old_price} to {new_price}".format(
                        name=product_data["name"],
                        old_price=previous_price,
                        new_price=new_price,
                    )
                )

    return "Update price archive\n\n{changes}".format(changes="\n".join(changes))


def _update_price_archive(
    products: list[Product], price_archive: list[Product]
) -> dict:
    """
    Return an updated version of the price archive.
    """
    updated_archive = copy.deepcopy(price_archive)

    # Keep a list of product codes for easier look-ups.
    archive_codes = [p["code"] for p in price_archive]

    # Loop over the new products and see if there are any new products or prices to add to the
    # archive.
    for product in products:
        # Is product in archive?
        try:
            index = archive_codes.index(product["code"])
        except ValueError:
            # Product isn't there - add it.
            archive_product = copy.deepcopy(product)
            updated_archive.append(archive_product)
        else:
            archive_product = price_archive[index]

        # See if there is a new price to add.
        # ..

        price_in_pounds = _convert_pence_to_pounds(product_data["price"])
        if product_id not in price_archive:
            # New product - not currently in archive.
            updated_archive[product_id] = {
                "name": product_data["name"],
                "prices": [
                    {
                        "date": price_date.isoformat(),
                        "price": price_in_pounds,
                    }
                ],
            }
        else:
            # Known product - see if price history needs updated.
            last_archived_price = price_archive[product_id]["prices"][-1]["price"]
            if price_in_pounds != last_archived_price:
                # Price is different from latest record - add a new record.
                updated_archive[product_id]["prices"].append(
                    {
                        "date": price_date.isoformat(),
                        "price": price_in_pounds,
                    }
                )

    return updated_archive


# Archive file handling


def _load_archive() -> list[Product]:
    """
    Load the product archive from file.
    """
    filepath = os.path.join(os.path.dirname(__file__), "prices.json")
    if not os.path.exists(filepath):
        return []

    with open(filepath, "r") as f:
        return json.load(f)


def _save_archive(archive: dict) -> None:
    filepath = os.path.join(os.path.dirname(__file__), "prices.json")
    with open(filepath, "w") as f:
        return json.dump(archive, f, indent=4)


def _convert_pence_to_pounds(pence: int) -> str:
    """
    Convert the passed amount in pence to a string in pounds.
    """
    amt = pence / 100
    return f"{amt:.2f}"


# Price fetching


def _fetch_product_prices(products: list[Product]) -> None:
    """
    Update the passed list of product data with retailer prices.
    """
    price_date = datetime.date.today()
    for product in products:
        for retailer_data in product["retailers"]:
            if retailer_data["retailer"] == "Ocado":
                price = _fetch_ocado_price(retailer_data["product_id"])
                retailer_data["prices"].append(
                    {"date": price_date.isoformat(), "price": price}
                )


class UnableToFetchPrice(Exception):
    pass


def _fetch_ocado_price(product_id: str) -> int:
    """
    Fetch the price of the passed product from Ocado.

    Raises UnableToFetchPrice.
    """
    # Construct URL for product detail page. The slug doesn't matter: Ocado will redirect to the
    # canonical URL.
    url = f"https://www.ocado.com/products/slug-{product_id}"

    # Fetch HTML content.
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        raise UnableToFetchPrice from e

    # Extract price from HTML content.
    try:
        return _extract_price(response.text)
    except UnableToExtractPrice as e:
        raise UnableToFetchPrice from e


class UnableToExtractPrice(Exception):
    pass


def _extract_price(content: str) -> int:
    """
    Return the price (in pence) from the passed HTML of a product detail page.
    """
    # Price is in <meta itemprop="price" ...> element.
    soup = bs4.BeautifulSoup(content, "html.parser")
    results = soup.find_all("meta", {"itemprop": "price"})
    if len(results) == 0:
        raise UnableToExtractPrice("No price element found in HTML")
    elif len(results) > 1:
        raise UnableToExtractPrice("Multiple price elements found in HTML")

    try:
        price_in_pounds = float(results[0]["content"])
    except ValueError as e:
        raise UnableToExtractPrice("Couldn't cast price to an int") from e

    return int(price_in_pounds * 100)


# Core


if __name__ == "__main__":
    main()
