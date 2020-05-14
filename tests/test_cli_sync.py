"""Test 'status' command"""
import os
import pytest
import git
from click.testing import CliRunner
import metarepo.cli
from tests import helpers


@pytest.fixture
def test_repo_and_workspace(tmpdir):
    """
    Create a repository with a few test commits and a
    workspace containing a configured manifest

    :param tmpdir: Directory where to create repo (provided by pytest automatically)
    :return: tuple of (repo object, path to workspace)
    """
    _, source_repo = helpers.create_commits(tmpdir / "source")
    workspace = tmpdir / "workspace"
    workspace.mkdir()

    helpers.create_manifest(workspace, {"repos": [{"uri": str(tmpdir / "source/.git"), "path": "test"}]})
    os.chdir(str(workspace))
    return source_repo, workspace


@pytest.fixture
def synced_repo_and_workspace(test_repo_and_workspace):
    """
    Builds upon 'test_repo_and_workspace' and also performs an initial sync
    :param test_repo_and_workspace:
    :return: (destination repo object, source repo object, path to workspace)
    """
    source_repo, workspace = test_repo_and_workspace
    result = CliRunner().invoke(metarepo.cli.cli, ["sync"])
    assert result.exit_code == 0

    dest_repo = git.Repo(workspace / "test")
    return dest_repo, source_repo, workspace


def test_sync_basic(test_repo_and_workspace):
    """Sync nonexistant repository"""
    source_repo, workspace = test_repo_and_workspace

    runner = CliRunner()
    result = runner.invoke(metarepo.cli.cli, ["sync"])
    assert result.exit_code == 0

    # Repo is created and is in sync
    dest_repo = git.Repo(workspace / "test")
    assert dest_repo.head.commit == source_repo.head.commit

    # Add additional commits
    helpers.write_and_commit(source_repo, "newfile.txt")

    # Repo no longer in sync
    assert dest_repo.head.commit != source_repo.head.commit

    # Sync
    result = runner.invoke(metarepo.cli.cli, ["sync"])
    assert dest_repo.head.commit == source_repo.head.commit
    assert result.exit_code == 0


def test_sync_dirty(synced_repo_and_workspace):
    """If repository is dirty, sync should stop"""
    _, _, workspace = synced_repo_and_workspace

    # Edit file in workspace
    (workspace / "test" / "output.txt").write(u"Changed")

    result = CliRunner().invoke(metarepo.cli.cli, ["sync"])
    assert result.exit_code == 1


def test_sync_ahead(synced_repo_and_workspace):
    """If repository is ahead origin sync should stop"""
    dest_repo, _, _ = synced_repo_and_workspace

    # Commit file in workspace
    helpers.write_and_commit(dest_repo, "output.txt")

    result = CliRunner().invoke(metarepo.cli.cli, ["sync"])
    assert result.exit_code == 1
