import io

import pytest

import main


class TestLoadProducts:
    def test_empty_dict(self):
        contents = io.StringIO("[]")

        assert main._load_products(contents) == []

    def test_single_product(self):
        contents = io.StringIO('[{"name": "X", "ocado_product_id": "123"}]')

        assert main._load_products(contents) == [
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
        contents = io.StringIO('[{"naem": "X", "ocado_product_id": "123"}]')

        with pytest.raises(main.InvalidJSON):
            main._load_products(contents)
