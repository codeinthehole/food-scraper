import datetime

from chow.usecases import charts
from tests import factories


class TestGenerateDataSeries:
    def test_single_price_change_with_matching_end_date(self):
        product_data = factories.ProductPriceHistory(
            prices=[
                factories.PriceChange(date="2022-10-01", price="1.00"),
            ]
        )
        end_date = datetime.date(2022, 10, 1)

        dates, prices = charts._generate_data_series(product_data, end_date)

        assert dates == [
            datetime.date(2022, 10, 1),
        ]
        assert prices == [1.00]

    def test_single_price_change_with_later_end_date(self):
        product_data = factories.ProductPriceHistory(
            prices=[
                factories.PriceChange(date="2022-10-01", price="1.00"),
            ]
        )
        end_date = datetime.date(2022, 10, 2)

        dates, prices = charts._generate_data_series(product_data, end_date)

        assert dates == [
            datetime.date(2022, 10, 1),
            datetime.date(2022, 10, 2),
        ]
        assert prices == [1.00, 1.00]

    def test_multiple_price_changes_with_later_end_date(self):
        product_data = factories.ProductPriceHistory(
            prices=[
                factories.PriceChange(date="2022-10-01", price="1.00"),
                factories.PriceChange(date="2022-10-03", price="2.00"),
            ]
        )
        end_date = datetime.date(2022, 10, 5)

        dates, prices = charts._generate_data_series(product_data, end_date)

        assert dates == [
            datetime.date(2022, 10, 1),
            datetime.date(2022, 10, 2),
            datetime.date(2022, 10, 3),
            datetime.date(2022, 10, 4),
            datetime.date(2022, 10, 5),
        ]
        assert prices == [1.00, 1.00, 2.00, 2.00, 2.00]
