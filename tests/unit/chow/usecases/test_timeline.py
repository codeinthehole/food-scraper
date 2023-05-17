from chow import archive
from chow.usecases import timeline as usecase
from tests import factories


class TestConvertToTimeline:
    def test_empty(self):
        archive_products: archive.ArchiveProductMap = {}

        timeline = usecase._convert_to_timeline(archive_products)

        assert timeline == []

    def test_single_product_single_price(self):
        archive_products: archive.ArchiveProductMap = {
            "sku_1": factories.ProductPriceHistory(
                name="Cheese",
                prices=[
                    factories.PriceChange(date="2021-01-10", price="0.70"),
                ],
            ),
        }

        timeline = usecase._convert_to_timeline(archive_products)

        assert timeline == [
            {
                "date": "2021-01-10",
                "event_descriptions": [
                    "🟡 Cheese added to archive - price is £0.70",
                ],
            }
        ]

    def test_multiple_products(self):
        archive_products: archive.ArchiveProductMap = {
            "sku_1": factories.ProductPriceHistory(
                name="Cheese",
                prices=[
                    factories.PriceChange(date="2021-01-10", price="0.70"),
                    factories.PriceChange(date="2021-02-10", price="0.90"),
                ],
            ),
            "sku_2": factories.ProductPriceHistory(
                name="Eggs",
                prices=[
                    factories.PriceChange(date="2021-01-10", price="1.20"),
                    factories.PriceChange(date="2021-02-10", price="1.35"),
                ],
            ),
        }

        timeline = usecase._convert_to_timeline(archive_products)

        assert timeline == [
            {
                "date": "2021-02-10",
                "event_descriptions": [
                    "🔴 Cheese changed price from £0.70 to £0.90 (+29%)",
                    "🔴 Eggs changed price from £1.20 to £1.35 (+13%)",
                ],
            },
            {
                "date": "2021-01-10",
                "event_descriptions": [
                    "🟡 Eggs added to archive - price is £1.20",
                    "🟡 Cheese added to archive - price is £0.70",
                ],
            },
        ]
