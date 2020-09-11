"""Test 'list' command"""
import os.path

import metarepo.cli
from click.testing import CliRunner
from tests import helpers


def test_list_no_manifest(tmpdir):
    """Manifest does not exist"""
    tmpdir.chdir()
    runner = CliRunner()
    result = runner.invoke(metarepo.cli.cli, ["list"])
    assert result.exit_code == 1
    assert "Not found" in result.output


def test_list_invalid_manifest(tmpdir):
    """Manifest is invalid"""
    helpers.create_manifest(tmpdir, {"whatever": []})
    tmpdir.chdir()
    runner = CliRunner()
    result = runner.invoke(metarepo.cli.cli, ["list"])
    assert result.exit_code == 1
    assert "Validation failed" in result.output


def test_list_basic(tmpdir):
    """List configured repos in manifest"""
    helpers.create_manifest(tmpdir, {"repos": [{"url": "http://localhost/repo", "path": "the/path"}]})
    tmpdir.chdir()
    runner = CliRunner()
    result = runner.invoke(metarepo.cli.cli, ["list"])
    assert result.exit_code == 0
    assert os.path.normpath("the/path") in result.output
    assert "http://localhost/repo" in result.output
