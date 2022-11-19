from unittest import mock

import pytest

from chow.usecases import price_fetching

# Don't run these tests by default. They are only needed when testing the direct integration with
# external sites.
pytestmark = pytest.mark.skip


class TestFetchOcadoPriceExternal:
    @pytest.mark.parametrize(
        "product_id, price",
        (
            ("13175011", 400),
            ("23476011", 190),
        ),
        ids=(
            "500g of Lurpak",
            "5 plain NY bagels",
        ),
    )
    def test_fetches_correct_price(self, product_id: str, price: int):
        assert (
            price_fetching._fetch_ocado_price(product_id, logger=mock.Mock()) == price
        )
