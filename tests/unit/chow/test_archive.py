import json

import pytest

from chow import archive


class TestLoad:
    def test_no_file(self):
        assert archive.load("/tmp/does-not-exist") == {}

    def test_empty_file(self, tmp_path):
        # Create file with empty dict content.
        archive_file = tmp_path / "prices.json"
        archive_file.write_text(json.dumps({}))

        assert archive.load(str(archive_file)) == {}

    def test_valid_file(self, tmp_path):
        # Create file with empty dict content.
        archive_file = tmp_path / "prices.json"
        content = {
            "123": {
                "name": "X",
                "prices": [
                    {"date": "2022-10-02", "price": "5.00"},
                ],
            },
        }
        archive_file.write_text(json.dumps(content))

        assert archive.load(str(archive_file)) == content

    def test_missing_prices(self, tmp_path):
        # Create file with empty dict content.
        archive_file = tmp_path / "prices.json"
        content = {
            "123": {
                "name": "X",
            },
        }
        archive_file.write_text(json.dumps(content))

        with pytest.raises(archive.InvalidJSON):
            archive.load(str(archive_file))

    def test_misspelt_name(self, tmp_path):
        # Create file with empty dict content.
        archive_file = tmp_path / "prices.json"
        content = {
            "123": {
                "mane": "X",
                "prices": [
                    {"date": "2022-10-02", "price": "5.00"},
                ],
            },
        }
        archive_file.write_text(json.dumps(content))

        with pytest.raises(archive.InvalidJSON):
            archive.load(str(archive_file)) == content

    def test_invalid_product_id(self, tmp_path):
        # Create file with empty dict content.
        archive_file = tmp_path / "prices.json"
        content = {
            "123x": {
                "name": "X",
                "prices": [
                    {"date": "2022-10-02", "price": "5.00"},
                ],
            },
        }
        archive_file.write_text(json.dumps(content))

        with pytest.raises(archive.InvalidJSON):
            archive.load(str(archive_file)) == content

    def test_extra_properties(self, tmp_path):
        # Create file with empty dict content.
        archive_file = tmp_path / "prices.json"
        content = {
            "123": {
                "name": "X",
                "egg": "X",
                "prices": [
                    {"date": "2022-10-02", "price": "5.00"},
                ],
            },
        }
        archive_file.write_text(json.dumps(content))

        with pytest.raises(archive.InvalidJSON):
            archive.load(str(archive_file)) == content
