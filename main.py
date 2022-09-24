import requests
import bs4


def main():
    pass


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


if __name__ == "__main__":
    main()
