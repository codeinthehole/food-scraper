import pytest

import main


class TestFetchOcadoPrice:
    @pytest.mark.parametrize(
        "product_id, price",
        (
            ("13175011", 500),
            ("23476011", 175),
        ),
        ids=(
            "500g of Lurpak",
            "5 plain NY bagels",
        ),
    )
    def test_fetches_correct_price(self, product_id: str, price: int):
        assert main._fetch_ocado_price(product_id) == price


class TestConvertPenceToPounds:
    @pytest.mark.parametrize(
        "price_in_pence, formatted_price",
        (
            (500, "5.00"),
            (175, "1.75"),
        ),
    )
    def test_conversion(self, price_in_pence: int, formatted_price: str):
        assert main._convert_pence_to_pounds(price_in_pence) == formatted_price
