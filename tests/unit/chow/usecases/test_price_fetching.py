from unittest import mock

import factory  # type:ignore
import pytest

from chow.usecases import price_fetching

# Factories


class ArchiveProductPrice(factory.DictFactory):
    date = "2022-09-20"
    price = "0.85"


class ArchiveProduct(factory.DictFactory):
    name = "Mars bar"
    prices = factory.List([ArchiveProductPrice()])


class Archive(factory.DictFactory):
    p1 = factory.SubFactory(ArchiveProduct)


class TestArchive:
    def test_defaults(self):
        assert Archive() == {
            "p1": {
                "name": "Mars bar",
                "prices": [{"date": "2022-09-20", "price": "0.85"}],
            }
        }


# Tests


class TestFetchOcadoPrice:
    @mock.patch.object(price_fetching.requests, "get")
    def test_extracts_correct_price(self, get, fixture):
        get.return_value = mock.Mock(text=fixture("ocado_product.html"))

        assert price_fetching._fetch_ocado_price(mock.sentinel.PRODUCT_ID) == 500


class TestConvertPenceToPounds:
    @pytest.mark.parametrize(
        "price_in_pence, formatted_price",
        (
            (500, "5.00"),
            (175, "1.75"),
        ),
    )
    def test_conversion(self, price_in_pence: int, formatted_price: str):
        assert (
            price_fetching._convert_pence_to_pounds(price_in_pence) == formatted_price
        )


class TestChangeSummary:
    def test_no_summary_when_no_changes(self):
        current_archive = {}
        updated_archive = {}

        assert price_fetching._change_summary(current_archive, updated_archive) == ""

    def test_summary_when_new_product_added(self):
        current_archive = {}
        updated_archive = Archive(p1__name="Snickers")

        summary = price_fetching._change_summary(current_archive, updated_archive)

        assert summary == "Update price archive\n\nNew product: Snickers"

    def test_summary_when_multiple_new_products_added(self):
        current_archive = {}
        updated_archive = Archive(
            p1=ArchiveProduct(name="Eggs"),
            p2=ArchiveProduct(name="Bacon"),
        )

        summary = price_fetching._change_summary(current_archive, updated_archive)

        assert (
            summary == "Update price archive\n\nNew product: Eggs\nNew product: Bacon"
        )

    def test_summary_when_product_removed(self):
        current_archive = Archive(
            p1=ArchiveProduct(name="Eggs"),
            p2=ArchiveProduct(name="Bacon"),
        )
        updated_archive = Archive(
            p1=ArchiveProduct(name="Eggs"),
        )

        summary = price_fetching._change_summary(current_archive, updated_archive)

        assert summary == "Update price archive\n\nRemove product: Bacon"

    def test_product_price_change(self):
        current_archive = Archive(
            p1=ArchiveProduct(
                name="Eggs",
                prices=[
                    ArchiveProductPrice(price="1.50"),
                ],
            )
        )
        updated_archive = Archive(
            p1=ArchiveProduct(
                name="Eggs",
                prices=[
                    ArchiveProductPrice(price="1.50"),
                    ArchiveProductPrice(price="2.50"),
                ],
            )
        )

        summary = price_fetching._change_summary(current_archive, updated_archive)

        assert (
            summary == "Update price archive\n\nPrice change for Eggs: £1.50 to £2.50"
        )
