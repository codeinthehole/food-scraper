import io

import pytest

import main


class TestLoadProducts:
    def test_empty_list(self):
        contents = io.StringIO("[]")

        assert main._load_products(contents) == []

    def test_single_product(self):
        contents = io.StringIO('[{"name": "X", "ocado_product_id": "123"}]')

        products = main._load_products(contents)

        assert products == [
            {
                "name": "X",
                "ocado_product_id": "123",
            }
        ]

    def test_invalid_json(self):
        contents = io.StringIO("this isn't JSON")

        with pytest.raises(main.InvalidJSON):
            main._load_products(contents)

    def test_missing_product_id_attribute(self):
        contents = io.StringIO('[{"name": "X"}]')

        with pytest.raises(main.InvalidJSON):
            main._load_products(contents)

    def test_misspelt_name_attribute(self):
        # No price attribute
        contents = io.StringIO('[{"naem": "X", "ocado_product_id": "123"}]')

        with pytest.raises(main.InvalidJSON):
            main._load_products(contents)

    def test_non_string_product_id(self):
        # No price attribute
        contents = io.StringIO('[{"name": "X", "ocado_product_id": 123}]')

        with pytest.raises(main.InvalidJSON):
            main._load_products(contents)
