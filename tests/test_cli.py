from click.testing import CliRunner

import multirepo.cli


def test_cli_basic(tmpdir):
    tmpdir.chdir()
    runner = CliRunner()
    result = runner.invoke(multirepo.cli.cli, ["info"])
    assert result.exit_code == 2
