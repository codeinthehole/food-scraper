import collections
import pathlib
from typing import TypedDict

from chow import archive, logger


class TimelineDate(TypedDict):
    date: str  # YYYY-MM-DD
    event_descriptions: list[str]


Timeline = list[TimelineDate]


def generate_timeline_file(
    archive_filepath: pathlib.Path,
    timeline_filepath: pathlib.Path,
    logger: logger.ConsoleLogger,
) -> None:
    """
    Generate a timeline document.
    """
    products_data = archive.load(str(archive_filepath))

    # Convert products data into timeline datastructure.
    timeline_data = _convert_to_timeline(products_data)

    missing_products = _generate_missing_products_summary(products_data)

    with timeline_filepath.open("w") as f:
        f.write("# Product price timeline\n")
        for timeline_date in timeline_data:
            line = f"## {timeline_date['date']}\n"
            for description in timeline_date["event_descriptions"]:
                line += f"{description}<br/>\n"
            f.write(line)

        if missing_products:
            f.write("## Missing products\n")
            f.write(f"{missing_products}\n")


def _generate_missing_products_summary(products_data: archive.ArchiveProductMap) -> str:
    """
    Return a summary of the products that are missing.
    """
    missing_product_names: list[str] = []
    for product_id, product_data in products_data.items():
        if product_data.get("removed", False):
            missing_product_names.append(product_data["name"])

    if not missing_product_names:
        return ""

    lines = ["The following products are no longer available:<br/>"]
    for name in sorted(missing_product_names):
        lines.append(f"- {name}")

    return "\n".join(lines)


def _convert_to_timeline(products_data: archive.ArchiveProductMap) -> Timeline:
    """
    Convert the archive data into a timeline structure where events are grouped by date.

    Events are sorted in reverse price-change percentage order.
    """
    # Convert archive data into a dict mapping the YYYY-MM-DD date string to a list of
    # (delta_percentage, change_description) tuples.
    grouped_changes: dict[str, list[tuple[float, str]]] = collections.defaultdict(list)
    for product_id, product_data in products_data.items():
        previous_price_change: archive.PriceChange | None = None
        # Prices are in chronological order.
        for price_change in product_data["prices"]:
            # Compute description of change.
            delta_percentage, change_description = _change_summary(
                product_id, product_data["name"], price_change, previous_price_change
            )

            grouped_changes[price_change["date"]].append(
                (delta_percentage, change_description)
            )
            previous_price_change = price_change

    # Sort in reverse chronological order.
    chronological_changes = sorted(list(grouped_changes.items()), reverse=True)

    # Build timeline datastructure.
    timeline = []
    for date, changes in chronological_changes:
        event_descriptions = [x[1] for x in sorted(changes, reverse=True)]
        timeline.append(TimelineDate(date=date, event_descriptions=event_descriptions))

    return timeline


def _change_summary(
    product_id: str,
    product_name: str,
    current_price_change: archive.PriceChange,
    previous_price_change: archive.PriceChange | None,
) -> tuple[float, str]:
    """
    Return a tuple of the price delta percentage and a summary of the price change.
    """
    product_url = f"./product-{product_id}.md"
    delta_percentage: float
    if previous_price_change is None:
        summary = f"🟡 [{product_name}]({product_url}) added to archive - price is £{current_price_change['price']}"
        delta_percentage = 0
    else:
        previous_price = float(previous_price_change["price"])
        current_price = float(current_price_change["price"])
        delta = current_price - previous_price
        delta_percentage = delta / previous_price * 100
        abs_delta_percentage = round(abs(delta) / previous_price * 100)
        summary = "{emoji} [{name}]({product_url}) changed price from £{previous_price} to £{current_price} ({sign}{abs_delta_percentage}%)".format(
            emoji="🔴" if delta > 0 else "🟢",
            name=product_name,
            product_url=product_url,
            previous_price=previous_price_change["price"],
            current_price=current_price_change["price"],
            sign="+" if delta > 0 else "-",
            abs_delta_percentage=abs_delta_percentage,
        )
    return delta_percentage, summary
