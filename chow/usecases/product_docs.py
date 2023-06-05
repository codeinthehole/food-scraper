import pathlib

from chow import archive, logger


def generate_product_detail_documents(
    archive_filepath: pathlib.Path,
    charts_folder: pathlib.Path,
    products_folder: pathlib.Path,
    logger: logger.ConsoleLogger,
) -> None:
    """
    Generate product detail documents in the passed folder.
    """
    products_data = archive.load(str(archive_filepath))
    for product_id, price_changes in products_data.items():
        document_filepath = products_folder / f"product-{product_id}.md"
        # TODO extract function for generating chart filepath.
        chart_filepath = charts_folder / f"product-{product_id}.png"
        chart_url = chart_filepath.relative_to(document_filepath.parent)
        with open(document_filepath, "w") as f:
            logger.debug(f"Writing {document_filepath}")
            f.write(_product_detail_markdown(price_changes, chart_url))


def _product_detail_markdown(
    price_changes: archive.ProductPriceHistory, chart_url: pathlib.Path
) -> str:
    """
    Return the markdown for a product detail document.
    """
    # Build a list of (date, description) lines in chronological order.
    date_descriptions: list[tuple[str, str]] = []
    previous_price: archive.PriceChange | None = None
    for price_change in price_changes["prices"]:
        if previous_price is not None:
            description = f"Changed price from £{previous_price['price']} to £{price_change['price']}"
        else:
            description = f"Added to archive with price £{price_change['price']}"
        date_descriptions.append((price_change["date"], description))
        previous_price = price_change

    # Sort in opposite order so most recent price changes are at the top.
    date_descriptions.reverse()

    # Build a list of markdown lines.
    lines = [f"# {price_changes['name']}", f"![]({chart_url})"]
    for date, description in date_descriptions:
        lines.append(f"## {date}")
        lines.append(description)

    return "\n".join(lines)
