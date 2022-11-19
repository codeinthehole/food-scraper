from tests import factories


class TestArchive:
    def test_defaults(self):
        assert factories.Archive() == {
            "p1": {
                "name": "Mars bar",
                "prices": [{"date": "2022-09-20", "price": "0.85"}],
            }
        }
