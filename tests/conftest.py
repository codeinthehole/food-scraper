import os
from collections.abc import Callable

import pytest


@pytest.fixture
def fixture_path() -> Callable[[str], str]:
    """
    Inject a function that looks up fixture filepaths.
    """

    def _path(relative_filepath: str) -> str:
        """
        Return the filepath to a fixture file.
        """
        filepath = os.path.join(
            os.path.dirname(__file__), "fixtures", relative_filepath
        )
        assert os.path.exists(filepath), f"Fixture {filepath} doesn't exist"
        return filepath

    return _path


@pytest.fixture
def fixture(fixture_path: Callable[[str], str]) -> Callable[[str], str]:
    """
    Inject a function that loads fixture file contents.
    """

    def _load_fixture(relative_filepath: str) -> str:
        """
        Return the contents of a fixture file.
        """
        with open(fixture_path(relative_filepath)) as f:
            return str(f.read())

    return _load_fixture
