import json

import time_machine

import chow.__main__ as main


def test_creates_product_doc(runner, fixture_path, tmp_path, tmp_path_factory):
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
        },
    }
    archive_file = tmp_path / "archive.json"
    archive_file.write_text(json.dumps(archive_data))

    # Create a throwaway folder to generate the product docs in.
    products_folder = tmp_path_factory.mktemp("products")

    # Create a charts folder within the docs folder with a single image in.
    charts_folder = products_folder / "charts"
    charts_folder.mkdir()
    chart_file = charts_folder / "product-123.png"
    chart_file.write_bytes(b"fake image data")

    # Run command.
    with time_machine.travel("2022-11-10T14:00"):
        result = runner.invoke(
            main.cli,
            args=[
                "generate-product-documents",
                str(archive_file),
                str(charts_folder),
                str(products_folder),
            ],
        )
    assert result.exit_code == 0, result.exception

    # Check a file has been created
    product_doc = products_folder / "product-123.md"
    assert product_doc.is_file()

    # Check the contents of the file
    with open(product_doc) as f:
        contents = f.read()
        lines = contents.splitlines()

    assert lines == [
        "# Crisps",
        "![](charts/product-123.png)",
        "**Note: This product is still available in the Ocado catalog.**",
        "## 2022-11-05",
        "🔴 Changed price from £3.00 to £4.00 (+33%)",
        "## 2022-11-01",
        "🟡 Added to archive with price £3.00",
    ]
