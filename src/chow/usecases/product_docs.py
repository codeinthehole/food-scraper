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
            # Determine % change.
            delta = float(price_change["price"]) - float(previous_price["price"])
            delta_percentage = delta / float(previous_price["price"]) * 100
            abs_delta_percentage = round(abs(delta_percentage))
            description = "{emoji} Changed price from £{previous_price} to £{current_price} ({sign}{abs_delta_percentage}%)".format(
                emoji="🔴" if delta > 0 else "🟢",
                previous_price=previous_price["price"],
                current_price=price_change["price"],
                sign="+" if delta > 0 else "-",
                abs_delta_percentage=abs_delta_percentage,
            )
        else:
            description = f"🟡 Added to archive with price £{price_change['price']}"
        date_descriptions.append((price_change["date"], description))
        previous_price = price_change

    # Sort in opposite order so most recent price changes are at the top.
    date_descriptions.reverse()

    # Build a list of markdown lines.
    lines = [f"# {price_changes['name']}", f"![]({chart_url})"]

    # Add removal status note
    if price_changes.get("removed", False):
        lines.append("**Note: This product has been removed from the Ocado catalog.**")
    else:
        lines.append("**Note: This product is still available in the Ocado catalog.**")

    for date, description in date_descriptions:
        lines.append(f"## {date}")
        lines.append(description)

    return "\n".join(lines)
