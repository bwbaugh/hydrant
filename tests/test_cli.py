import click.testing
import pytest

from hydrant import cli


@pytest.fixture
def runner():
    return click.testing.CliRunner()


def test_smoke(runner):
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert not result.exception
