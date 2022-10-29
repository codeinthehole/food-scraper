import copy
import datetime
import json
import os
from typing import Any

import bs4
import requests


def main() -> None:
    """
    Update a price archive JSON file.
    """
    # Declare products to track. This maps Ocado's product ID to a product description.
    # TODO make this a separate file that is passed in.
    products: dict[str, dict[str, Any]] = {
        "13175011": {"name": "Lurpak butter (500g)"},
        "23476011": {"name": "New York bagels (5)"},
        "65448011": {"name": "Brown onions (3 pack)"},
        "64861011": {"name": "Royal Gala apples (6 pack)"},
        "44855011": {"name": "Fairtrade bananas (5 pack)"},
        "78914011": {"name": "Semi skimmed milk (4 pints)"},
        "57293011": {"name": "Large free range eggs (6 pack)"},
        "53687011": {"name": "Blueberries (150g)"},
        "47305011": {"name": "Lemons (5 pack)"},
        "91370011": {"name": "Large garlic"},
        "96798011": {"name": "Red seedless grapes (500g)"},
        "240875011": {"name": "Cucumber"},
        "31833011": {"name": "Cathedral City Cheese (550g)"},
        "510737011": {"name": "Super seeded loaf (800g)"},
        "321394011": {"name": "Helda stringless beans (180g)"},
        "225627011": {"name": "Chicken thigh fillets (450g)"},
        "32003011": {"name": "Onken biopot natural yoghurt (1kg)"},
        "98385011": {"name": "Parmigiano reggiano (320g)"},
    }

    # Append latest price to products dict.
    _fetch_product_prices(products)

    # Update archive file.
    current_archive = _load_archive()
    updated_archive = _update_price_archive(
        price_date=datetime.date.today(),
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
                    "Price change for {name}: £{old_price} to £{new_price}".format(
                        name=product_data["name"],
                        old_price=previous_price,
                        new_price=new_price,
                    )
                )

    return "Update price archive\n\n{changes}".format(changes="\n".join(changes))


def _update_price_archive(
    price_date: datetime.date, products: dict[str, dict[str, Any]], price_archive: dict
) -> dict:
    """
    Return an updated version of the price archive.
    """
    updated_archive = copy.deepcopy(price_archive)
    for product_id, product_data in products.items():
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


def _load_archive() -> dict:
    # Format:
    #
    # {
    #     13175011: {
    #         "name": "xxx",
    #         "prices": [
    #             {
    #                 "date": "2020-09-22":
    #                 "price": "5.00",
    #             }
    #         ]
    #     }
    # }
    filepath = os.path.join(os.path.dirname(__file__), "prices.json")
    if not os.path.exists(filepath):
        return {}

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


def _fetch_product_prices(products: dict[str, dict[str, Any]]) -> None:
    """
    Update the passed dict of product data with latest prices.
    """
    for product_id, product_data in products.items():
        product_data["price"] = _fetch_ocado_price(product_id)


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
