import pathlib

from chow.usecases import product_docs as usecase
from tests import factories


class TestProductDetailMarkdown:
    def test_product_not_removed(self):
        price_changes = factories.ProductPriceHistory(
            name="Test Product",
            removed=False,
            prices=[
                factories.PriceChange(date="2021-01-10", price="1.50"),
            ],
        )
        chart_url = pathlib.Path("chart.png")

        result = usecase._product_detail_markdown(price_changes, chart_url)

        expected_lines = [
            "# Test Product",
            "![](chart.png)",
            "**Note: This product is still available in the Ocado catalog.**",
            "## 2021-01-10",
            "🟡 Added to archive with price £1.50",
        ]
        assert result == "\n".join(expected_lines)

    def test_product_removed(self):
        price_changes = factories.ProductPriceHistory(
            name="Removed Product",
            removed=True,
            prices=[
                factories.PriceChange(date="2021-01-10", price="2.00"),
            ],
        )
        chart_url = pathlib.Path("chart.png")

        result = usecase._product_detail_markdown(price_changes, chart_url)

        expected_lines = [
            "# Removed Product",
            "![](chart.png)",
            "**Note: This product has been removed from the Ocado catalog.**",
            "## 2021-01-10",
            "🟡 Added to archive with price £2.00",
        ]
        assert result == "\n".join(expected_lines)

    def test_product_without_removed_field_defaults_to_available(self):
        price_changes = factories.ProductPriceHistory(
            name="Default Product",
            prices=[
                factories.PriceChange(date="2021-01-10", price="3.00"),
            ],
        )
        chart_url = pathlib.Path("chart.png")

        result = usecase._product_detail_markdown(price_changes, chart_url)

        expected_lines = [
            "# Default Product",
            "![](chart.png)",
            "**Note: This product is still available in the Ocado catalog.**",
            "## 2021-01-10",
            "🟡 Added to archive with price £3.00",
        ]
        assert result == "\n".join(expected_lines)
