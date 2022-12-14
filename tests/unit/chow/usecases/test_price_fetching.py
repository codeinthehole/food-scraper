from unittest import mock

import pytest

from chow import archive
from chow.usecases import price_fetching
from tests import factories


class TestFetchOcadoPrice:
    @mock.patch.object(price_fetching.requests, "get")
    def test_extracts_correct_price(self, get, fixture):
        get.return_value = mock.Mock(text=fixture("ocado_product.html"))

        price = price_fetching._fetch_ocado_price(
            mock.sentinel.PRODUCT_ID, logger=mock.Mock()
        )
        assert price == 500


class TestConvertPenceToPounds:
    @pytest.mark.parametrize(
        "price_in_pence, formatted_price",
        (
            (500, "5.00"),
            (175, "1.75"),
        ),
    )
    def test_conversion(self, price_in_pence: int, formatted_price: str) -> None:
        assert (
            price_fetching._convert_pence_to_pounds(price_in_pence) == formatted_price
        )


class TestChangeSummary:
    def test_no_summary_when_no_changes(self):
        current_archive: archive.ArchiveProductMap = {}
        updated_archive: archive.ArchiveProductMap = {}

        assert price_fetching._change_summary(current_archive, updated_archive) == ""

    def test_summary_when_new_product_added(self):
        current_archive: archive.ArchiveProductMap = {}
        updated_archive = factories.Archive(p1__name="Snickers")

        summary = price_fetching._change_summary(current_archive, updated_archive)

        assert summary == "Update price archive\n\nNew product: Snickers"

    def test_summary_when_multiple_new_products_added(self):
        current_archive: archive.ArchiveProductMap = {}
        updated_archive = factories.Archive(
            p1=factories.ArchiveProduct(name="Eggs"),
            p2=factories.ArchiveProduct(name="Bacon"),
        )

        summary = price_fetching._change_summary(current_archive, updated_archive)

        assert (
            summary == "Update price archive\n\nNew product: Eggs\nNew product: Bacon"
        )

    def test_summary_when_product_removed(self):
        current_archive = factories.Archive(
            p1=factories.ArchiveProduct(name="Eggs"),
            p2=factories.ArchiveProduct(name="Bacon"),
        )
        updated_archive = factories.Archive(
            p1=factories.ArchiveProduct(name="Eggs"),
        )

        summary = price_fetching._change_summary(current_archive, updated_archive)

        assert summary == "Update price archive\n\nRemove product: Bacon"

    def test_product_price_change(self):
        current_archive = factories.Archive(
            p1=factories.ArchiveProduct(
                name="Eggs",
                prices=[
                    factories.ArchiveProductPrice(price="1.50"),
                ],
            )
        )
        updated_archive = factories.Archive(
            p1=factories.ArchiveProduct(
                name="Eggs",
                prices=[
                    factories.ArchiveProductPrice(price="1.50"),
                    factories.ArchiveProductPrice(price="2.50"),
                ],
            )
        )

        summary = price_fetching._change_summary(current_archive, updated_archive)

        assert (
            summary == "Update price archive\n\nPrice change for Eggs: ??1.50 to ??2.50"
        )
