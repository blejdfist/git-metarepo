"""Test 'status' command"""
import re
from click.testing import CliRunner
import multirepo.cli
from tests import helpers

TEST_MANIFEST_ORIGIN = "http://localhost/nop"
TEST_MANIFEST = {"repos": [{"uri": TEST_MANIFEST_ORIGIN, "path": "the_repo"}]}


def test_status_not_found(tmpdir):
    """Configure repo does not exist"""
    helpers.create_manifest(tmpdir, TEST_MANIFEST)
    tmpdir.chdir()

    runner = CliRunner()
    result = runner.invoke(multirepo.cli.cli, ["status"])
    assert result.exit_code == 0
    assert "NOT FOUND" in result.output


def test_status_exists(tmpdir):
    """Configure repo exist and is clean"""
    helpers.create_commits(tmpdir.join("the_repo"), TEST_MANIFEST_ORIGIN)
    helpers.create_manifest(tmpdir, TEST_MANIFEST)
    tmpdir.chdir()

    runner = CliRunner()
    result = runner.invoke(multirepo.cli.cli, ["status"])
    assert result.exit_code == 0
    assert re.search(r"head:.{0,5}master", result.output)
    assert re.search(r"dirty:.{0,5}False", result.output)


def test_status_exists_dirty(tmpdir):
    """Configured repo exist and is dirty"""
    helpers.create_commits(tmpdir.join("the_repo"), TEST_MANIFEST_ORIGIN)
    helpers.create_manifest(tmpdir, TEST_MANIFEST)

    tmpdir.join("the_repo").join("output.txt").write("Hello")
    tmpdir.chdir()

    runner = CliRunner()
    result = runner.invoke(multirepo.cli.cli, ["status"])
    assert result.exit_code == 0
    assert re.search(r"head:.{0,5}master", result.output)
    assert re.search(r"dirty:.{0,5}True", result.output)


def test_status_in_repo_subdirectory(tmpdir):
    """Run status in a subdirectory of a repo should still work"""
    helpers.create_commits(tmpdir)
    helpers.create_manifest(tmpdir, TEST_MANIFEST)

    tmpdir.mkdir("some").mkdir("folder").chdir()

    runner = CliRunner()
    result = runner.invoke(multirepo.cli.cli, ["status"])
    assert result.exit_code == 0
    assert "the_repo" in result.output


def test_status_invalid_repository(tmpdir):
    """Configured repo is invalid (just an empty folder)"""
    tmpdir.mkdir("the_repo")
    helpers.create_manifest(tmpdir, TEST_MANIFEST)
    tmpdir.chdir()

    runner = CliRunner()
    result = runner.invoke(multirepo.cli.cli, ["status"])
    assert result.exit_code == 0
    assert "INVALID" in result.output


def test_status_wrong_origin(tmpdir):
    """Configured repo has the wrong origin"""
    helpers.create_commits(tmpdir.mkdir("the_repo"), "http://other/origin")
    helpers.create_manifest(tmpdir, TEST_MANIFEST)
    tmpdir.chdir()

    runner = CliRunner()
    result = runner.invoke(multirepo.cli.cli, ["status"])
    assert result.exit_code == 0
    assert "ORIGIN MISMATCH" in result.output


def test_status_no_recurse_on_folder(tmpdir):
    """Workspace is a repository and the configure repository is just an empty folder
    Should report the repo as invalid and not recursively search in parents"""
    helpers.create_commits(tmpdir)
    helpers.create_manifest(tmpdir, TEST_MANIFEST)
    tmpdir.chdir()

    # Repository is just an empty folder
    tmpdir.mkdir("the_repo")

    runner = CliRunner()
    result = runner.invoke(multirepo.cli.cli, ["status"])
    assert result.exit_code == 0
    assert "INVALID" in result.output


def test_status_no_recurse_on_file(tmpdir):
    """Workspace is a repository and the configure repository is just a file
    Should report the repo as invalid and not recursively search in parents"""
    helpers.create_commits(tmpdir)
    helpers.create_manifest(tmpdir, TEST_MANIFEST)

    # Repository is just an empty folder
    tmpdir.join("the_repo").write("")
    tmpdir.chdir()

    runner = CliRunner()
    result = runner.invoke(multirepo.cli.cli, ["status"])
    assert result.exit_code == 0
    assert "INVALID" in result.output
