import datetime
import pathlib

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from chow import archive, logger


def generate_product_graphs(
    archive_filepath: pathlib.Path,
    chart_folder: pathlib.Path,
    logger: logger.ConsoleLogger,
) -> None:
    """
    Generate price graph images for each produce in the passed archive file.
    """
    archive_data = archive.load(str(archive_filepath))
    for product_id, product_data in archive_data.items():
        filepath = f"{chart_folder}/product-{product_id}.png"
        _generate_product_graph(product_data, filepath)


def _generate_product_graph(
    product_data: archive.ProductPriceHistory, filepath: str
) -> None:
    """
    Generate a price chart PNG file in the passed filepath.
    """
    # Extract data series.
    dates, prices = _generate_data_series(product_data, end_date=datetime.date.today())

    # Create graph object. The generated PNGs are 640x480 pixels.
    figure, axes = plt.subplots()
    axes.plot(np.array(dates), prices, linestyle="--", marker="o")
    axes.set_title(product_data["name"])
    axes.set_xlabel("Date")
    axes.set_ylabel("Price")

    # Ensure X axis has sensible ticks.
    locator = mdates.AutoDateLocator(minticks=3, maxticks=15)
    formatter = mdates.ConciseDateFormatter(locator)
    axes.xaxis.set_major_locator(locator)  # type: ignore[attr-defined]
    axes.xaxis.set_major_formatter(formatter)  # type: ignore[attr-defined]

    # Ensure Y axis starts at zero and has fixed precision.
    plt.ylim(0, max(prices) + 1)
    axes.yaxis.set_major_formatter(  # type: ignore[attr-defined]
        ticker.FormatStrFormatter("£%.2f")
    )

    # Save to file.
    figure.savefig(filepath)

    plt.close()


def _generate_data_series(
    product_data: archive.ProductPriceHistory, end_date: datetime.date
) -> tuple[list[datetime.date], list[float]]:
    """
    Return data series based on the product price-change data.
    """
    dates: list[datetime.date] = []
    prices: list[float] = []

    for price_change in product_data["prices"]:
        date = datetime.date.fromisoformat(price_change["date"])
        price = float(price_change["price"])
        if len(dates) == 0:
            # First iteration, add first data point.
            dates.append(date)
            prices.append(price)
        else:
            # Fill in dates and prices for gap.
            previous_date = dates[-1]
            previous_price = prices[-1]
            delta = date - previous_date
            for x in range(1, delta.days):
                dates.append(previous_date + datetime.timedelta(days=x))
                prices.append(previous_price)

            # Add price change point.
            dates.append(date)
            prices.append(price)

    # Append price points up to today's date.
    final_delta = end_date - date
    for x in range(1, final_delta.days + 1):
        dates.append(date + datetime.timedelta(days=x))
        prices.append(price)

    return dates, prices
