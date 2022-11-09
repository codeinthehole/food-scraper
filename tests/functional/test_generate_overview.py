import json
import shutil

import time_machine

import main


def test_creates_overview_doc(runner, fixture_path, tmp_path, tmp_path_factory):
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

    # Create a throwaway folder to generate the overview doc in.
    overview_folder = tmp_path_factory.mktemp("docs")
    overview_file = overview_folder / "overview.md"

    # Create a charts folder in the above temp folder and copy a product image into it.
    charts_folder = overview_folder / "charts"
    charts_folder.mkdir()
    shutil.copyfile(fixture_path("product.png"), str(charts_folder / "product-123.png"))

    # Run command.
    with time_machine.travel("2022-11-10T14:00"):
        result = runner.invoke(
            main.cli,
            args=[
                "generate-overview",
                str(archive_file),
                str(charts_folder),
                str(overview_file),
            ],
        )
    assert result.exit_code == 0, result.exception

    # Check overview file has been created.
    assert overview_file.exists()

    # Check contents are correct.
    with open(overview_file) as f:
        contents = f.read()

    assert contents == "# Product price charts\n![Crisps](charts/product-123.png)\n"
