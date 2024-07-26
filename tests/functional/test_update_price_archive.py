import json
import re

import responses
import time_machine

import chow.__main__ as main


@responses.activate
def test_create_archive_file(runner, fixture, tmp_path):
    # Create a temporary file of products.
    products = [{"name": "Crisps", "ocado_product_id": "123"}]
    products_file = tmp_path / "products.json"
    products_file.write_text(json.dumps(products))

    # Create a filepath for the archive file
    archive_file = tmp_path / "archive.json"

    # Stub Ocado response for the above product URL.
    responses.get(
        url=re.compile(r"https://www.ocado.com/products/slug-123"),
        body=fixture("ocado_product.html"),
    )

    # Run command.
    with time_machine.travel("2022-11-01T14:00"):
        result = runner.invoke(
            main.cli,
            args=["update-price-archive", str(products_file), str(archive_file)],
        )
    assert result.exit_code == 0, result.output

    # Check archive file has been created.
    content = json.loads(archive_file.read_text())
    assert content == {
        "123": {
            "name": "Crisps",
            "prices": [
                {
                    "date": "2022-11-01",
                    "price": "5.00",
                }
            ],
        }
    }


@responses.activate
def test_update_archive_file(runner, fixture, tmp_path):
    # Create a temporary file of products.
    products = [{"name": "Crisps", "ocado_product_id": "123"}]
    products_file = tmp_path / "products.json"
    products_file.write_text(json.dumps(products))

    # Create an archive file with a pre-existing price.
    archive_data = {
        "123": {
            "name": "Crisps",
            "prices": [
                {
                    "date": "2022-11-01",
                    "price": "3.00",  # Different price from fixture.
                }
            ],
        }
    }
    archive_file = tmp_path / "archive.json"
    archive_file.write_text(json.dumps(archive_data))

    # Stub Ocado response for any the above product URL.
    responses.get(
        url=re.compile(r"https://www.ocado.com/products/slug-123"),
        body=fixture("ocado_product.html"),
    )

    # Run command at a later date then archived price.
    with time_machine.travel("2022-11-03T14:00"):
        result = runner.invoke(
            main.cli,
            args=["update-price-archive", str(products_file), str(archive_file)],
        )
    assert result.exit_code == 0, result.output

    # Check archive file has been updated correctly.
    content = json.loads(archive_file.read_text())
    assert content == {
        "123": {
            "name": "Crisps",
            "prices": [
                {
                    "date": "2022-11-01",
                    "price": "3.00",
                },
                {
                    "date": "2022-11-03",
                    "price": "5.00",
                },
            ],
        }
    }
