import main

import pytest


class TestFetchOcadoPrice:

    @pytest.mark.parametrize(
        "product_id, price",
        (
            (13175011, 500),
            (23476011, 175),
        ),
        ids=(
            "500g of Lurpak",
            "5 plain NY bagels",
        )
    )
    def test_fetches_correct_price(self, product_id: int, price: int):
        assert main._fetch_ocado_price(product_id) == price, product_description
