import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    yield CliRunner(
        # Pass default env vars.
        env=dict()
    )
