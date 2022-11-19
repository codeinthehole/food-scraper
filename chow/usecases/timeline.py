import collections
import pathlib
from typing import List, Optional, TypedDict

from chow import archive, logger


class TimelineDate(TypedDict):
    date: str  # YYYY-MM-DD
    event_descriptions: List[str]


Timeline = List[TimelineDate]


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

    with timeline_filepath.open("w") as f:
        f.write("# Product price timeline\n")
        for timeline_date in timeline_data:
            line = f"## {timeline_date['date']}\n"
            for description in timeline_date["event_descriptions"]:
                line += f"- {description}\n"
            f.write(line)


def _convert_to_timeline(products_data: archive.ArchiveProductMap) -> Timeline:
    """
    Convert the archive data into a timeline structure where events are grouped by date.
    """
    grouped_changes = collections.defaultdict(list)
    for product_data in products_data.values():
        previous_price_change: Optional[archive.PriceChange] = None
        for price_change in product_data["prices"]:
            grouped_changes[price_change["date"]].append(
                _change_summary(
                    product_data["name"], price_change, previous_price_change
                )
            )
            previous_price_change = price_change

    # Sort in reverse chronological order.
    sorted_changes = sorted(list(grouped_changes.items()), reverse=True)

    return [
        {"date": date, "event_descriptions": changes}
        for (date, changes) in sorted_changes
    ]


def _change_summary(
    product_name: str,
    current_price_change: archive.PriceChange,
    previous_price_change: Optional[archive.PriceChange],
) -> str:
    if previous_price_change is None:
        summary = f"{product_name} added to archive - price is £{current_price_change['price']}"
    else:
        previous_price = float(previous_price_change["price"])
        current_price = float(current_price_change["price"])
        delta = current_price - previous_price
        delta_percentage = round(abs(delta) / previous_price * 100)
        summary = "{name} changed price from £{previous_price} to £{current_price} ({sign}{delta_percentage}%)".format(
            name=product_name,
            previous_price=previous_price_change["price"],
            current_price=current_price_change["price"],
            sign="+" if delta > 0 else "-",
            delta_percentage=delta_percentage,
        )
    return summary
