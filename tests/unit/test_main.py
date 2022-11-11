import io

import pytest

import main


class TestLoadProducts:
    def test_empty_dict(self):
        contents = io.StringIO("{}")

        assert main._load_products(contents) == {}

    def test_single_product(self):
        contents = io.StringIO('{"123": {"name": "X", "price": null}}')

        product_map = main._load_products(contents)

        assert product_map == {
            "123": {
                "name": "X",
                "price": None,
            }
        }

    def test_invalid_json(self):
        contents = io.StringIO("this isn't JSON")

        with pytest.raises(main.InvalidJSON):
            main._load_products(contents)

    def test_missing_price_attribute(self):
        # No price attribute
        contents = io.StringIO('{"123": {"name": "X"}}')

        with pytest.raises(main.InvalidJSON):
            main._load_products(contents)

    def test_misspelt_name_attribute(self):
        # No price attribute
        contents = io.StringIO('{"123": {"mane": "X", "price": null}}')

        with pytest.raises(main.InvalidJSON):
            main._load_products(contents)

    def test_non_numeric_key(self):
        # No price attribute
        contents = io.StringIO('{"123x": {"mane": "X", "price": null}}')

        with pytest.raises(main.InvalidJSON):
            main._load_products(contents)
