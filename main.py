import sys
import requests
import bs4
import datetime
from decimal import Decimal as D


def main() -> None:
    """
    Write a summary of prices to STDOUT.
    """
    today = datetime.date.today()

    # Products to track.
    products: dict[int, str] = {
        13175011: "Lurpak butter (500g)",
        23476011: "New York bagels (5)",
    }

    for product_id, product_description in products.items():
        price_in_pence = _fetch_ocado_price(product_id)

        # Format line
        price_in_pounds = _convert_pence_to_pounds(price_in_pence)
        line = f"{product_id} - {product_description} - £{price_in_pounds}"

        sys.stdout.write(line + "\n")


def _convert_pence_to_pounds(pence: int) -> str:
    """
    Convert the passed amount in pence to a string in pounds.
    """
    amt = pence / 100
    return f"{amt:.2f}"


# Price fetching


class UnableToFetchPrice(Exception):
    pass


def _fetch_ocado_price(product_id: int) -> int:
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
        return _extract_price(response.content)
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
