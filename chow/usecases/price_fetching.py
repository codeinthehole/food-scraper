import concurrent.futures
import copy
import datetime
from typing import TypedDict

import bs4
import requests

from chow import archive, logger


class Product(TypedDict):
    name: str
    ocado_product_id: str


Products = list[Product]

# A private type associating prices with products.
_ProductPrices = list[tuple[Product, int]]


def update_price_archive(
    products: Products, archive_filepath: str, logger: logger.ConsoleLogger
) -> str:
    """
    Fetch prices for the passed products and update the price archive.
    """
    # Fetch product prices.
    product_prices = _fetch_product_prices(products, logger)

    # Update archive file.
    current_archive = archive.load(archive_filepath)
    updated_archive = _update_price_archive(
        price_date=datetime.date.today(),
        product_prices=product_prices,
        price_archive=current_archive,
    )

    # If the archive has changed, save it and print out a summary of changes.
    if updated_archive != current_archive:
        archive.save(archive_filepath, updated_archive)
        return _change_summary(current_archive, updated_archive)

    return ""


def _fetch_product_prices(
    products: Products, logger: logger.ConsoleLogger
) -> _ProductPrices:
    """
    Return a list of product prices.
    """
    # Use a thread pool to fetch prices concurrently.
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Create a dict of Future->Product
        future_to_data = {
            executor.submit(
                _fetch_ocado_price, product["ocado_product_id"], logger
            ): product
            for product in products
        }

        # Loop over the completed futures and update the product data dict.
        product_prices: _ProductPrices = []
        for future in concurrent.futures.as_completed(future_to_data):
            product = future_to_data[future]
            try:
                price = future.result()
            except UnableToFetchPrice as e:
                logger.error(
                    "Unable to fetch price for product %s: %s" % (product["name"], e)
                )
            else:
                product_prices.append((product, price))

    return product_prices


class UnableToFetchPrice(Exception):
    pass


def _fetch_ocado_price(product_id: str, logger: logger.ConsoleLogger) -> int:
    """
    Fetch the price of the passed product from Ocado.

    Raises UnableToFetchPrice.
    """
    logger.info(f"Fetching price for product {product_id}")

    # Construct URL for product detail page. The slug doesn't matter: Ocado will redirect to the
    # canonical URL.
    url = f"https://www.ocado.com/products/slug-{product_id}"

    # Fetch HTML content.
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        raise UnableToFetchPrice(str(e))

    # Extract price from HTML content.
    try:
        return _extract_price(response.text)
    except UnableToExtractPrice as e:
        raise UnableToFetchPrice(str(e))


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


def _update_price_archive(
    price_date: datetime.date,
    product_prices: _ProductPrices,
    price_archive: archive.ArchiveProductMap,
) -> archive.ArchiveProductMap:
    """
    Return an updated version of the price archive.
    """
    # Create a new copy of the archive.
    updated_archive = copy.deepcopy(price_archive)
    for product, price in product_prices:
        price_in_pounds = _convert_pence_to_pounds(price)
        product_id = product["ocado_product_id"]
        if product_id not in price_archive:
            # New product - not currently in archive.
            updated_archive[product_id] = {
                "name": product["name"],
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


def _convert_pence_to_pounds(pence: int) -> str:
    """
    Convert the passed amount in pence to a string in pounds.
    """
    amt = pence / 100
    return f"{amt:.2f}"


def _change_summary(
    current_archive: archive.ArchiveProductMap,
    updated_archive: archive.ArchiveProductMap,
) -> str:
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
