"""Test of CLI commands"""
import yaml
from click.testing import CliRunner
import multirepo.cli
from tests import helpers


def test_cli_no_manifest(tmpdir):
    """Test listing of configured meta repositories"""
    tmpdir.chdir()
    runner = CliRunner()
    result = runner.invoke(multirepo.cli.cli, ["info"])
    assert result.exit_code == 1


def test_cli_status_not_found(tmpdir):
    """Configure repo does not exist"""
    manifest = {"repos": [{"uri": "http://localhost/nop", "path": "the_repo"}]}

    tmpdir.join("manifest.yml").write(yaml.dump(manifest))
    tmpdir.chdir()

    runner = CliRunner()
    result = runner.invoke(multirepo.cli.cli, ["status"])
    assert result.exit_code == 0
    assert result.output.find("E:NOT FOUND") != -1


def test_cli_status_exists(tmpdir):
    """Configure repo exist and is clean"""
    manifest = {"repos": [{"uri": "http://localhost/nop", "path": "the_repo"}]}

    helpers.create_commits(tmpdir.join("the_repo"), "http://localhost/nop")

    tmpdir.join("manifest.yml").write(yaml.dump(manifest))
    tmpdir.chdir()

    runner = CliRunner()
    result = runner.invoke(multirepo.cli.cli, ["status"])
    assert result.exit_code == 0
    assert result.output.find("master") != -1
