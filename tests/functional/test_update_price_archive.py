import json
import re

import responses
import time_machine

import main


@responses.activate
def test_create_archive_file(runner, tmp_path):
    # Create a temporary file of products.
    products = {"123": {"name": "Crisps", "price": None}}
    products_file = tmp_path / "products.json"
    products_file.write_text(json.dumps(products))

    # Create a filepath for the archive file
    archive_file = tmp_path / "archive.json"

    # Stub Ocado response for any the above product URL.
    with open("tests/fixtures/ocado_product.html") as f:
        response_html = f.read()
    responses.get(
        url=re.compile(r"https://www.ocado.com/products/slug-123"),
        body=response_html,
    )

    # Run command.
    with time_machine.travel("2022-11-01T14:00"):
        result = runner.invoke(
            main.cli,
            args=["update-price-archive", str(products_file), str(archive_file)],
        )
    assert result.exit_code == 0, result.exception

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
def test_update_archive_file(runner, tmp_path):
    # Create a temporary file of products.
    products = {"123": {"name": "Crisps", "price": None}}
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
    with open("tests/fixtures/ocado_product.html") as f:
        response_html = f.read()
    responses.get(
        url=re.compile(r"https://www.ocado.com/products/slug-123"),
        body=response_html,
    )

    # Run command at a later date then archived price.
    with time_machine.travel("2022-11-03T14:00"):
        result = runner.invoke(
            main.cli,
            args=["update-price-archive", str(products_file), str(archive_file)],
        )
    assert result.exit_code == 0, result.exception

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
