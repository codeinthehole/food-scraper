import pathlib

from chow import archive, logger


def generate_overview_file(
    archive_filepath: pathlib.Path,
    charts_folder: pathlib.Path,
    overview_filepath: pathlib.Path,
    logger: logger.ConsoleLogger,
) -> None:
    """
    Generate an overview markdown file.
    """
    products_data = archive.load(str(archive_filepath))

    with overview_filepath.open("w") as f:
        f.write("# Product price charts\n")

        for product_id, product_data in products_data.items():
            image_file = charts_folder / f"product-{product_id}.png"
            if not image_file.exists():
                continue
            image_url = image_file.relative_to(overview_filepath.parent)
            # Size images so they float two per row.
            line = '<img align="left" style="width:48%" alt="{name}" src="{image_url}" />\n'.format(
                name=product_data["name"], image_url=str(image_url)
            )
            f.write(line)
