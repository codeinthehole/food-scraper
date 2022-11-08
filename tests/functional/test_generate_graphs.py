import json

import time_machine

import main


def test_creates_product_graphs(runner, tmp_path, tmp_path_factory):
    # Create an archive file with a product with some prices
    archive_data = {
        "123": {
            "name": "Crisps",
            "prices": [
                {
                    "date": "2022-11-01",
                    "price": "3.00",
                },
                {
                    "date": "2022-11-05",
                    "price": "4.00",
                },
            ],
        }
    }
    archive_file = tmp_path / "archive.json"
    archive_file.write_text(json.dumps(archive_data))

    # Create a folder to put the images in.
    charts_folder = tmp_path_factory.mktemp("charts")

    # Run command a few days after latest price change.
    with time_machine.travel("2022-11-10T14:00"):
        result = runner.invoke(
            main.cli,
            args=["generate-graphs", str(archive_file), str(charts_folder)],
        )
    assert result.exit_code == 0, result.exception

    # Check chart image file has been created
    chart_path = charts_folder / "product-123.png"
    assert chart_path.exists()
