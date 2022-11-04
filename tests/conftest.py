import os
from typing import Callable

import pytest


@pytest.fixture
def fixture() -> Callable[[str], str]:
    def _load_fixture(relative_filepath: str):
        """
        Return the contents of a fixture file.
        """
        filepath = os.path.join(
            os.path.dirname(__file__), "fixtures", relative_filepath
        )
        assert os.path.exists(filepath), f"Fixture {filepath} doesn't exist"

        with open(filepath, "r") as f:
            return f.read()

    return _load_fixture
