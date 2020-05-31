"""Test 'status' command"""
import os

import git
import metarepo.cli
import pytest
from click.testing import CliRunner
from tests import helpers


@pytest.fixture(name="test_repo_and_workspace")
def fixture_test_repo_and_workspace(tmpdir):
    """
    Create a repository with a few test commits and a
    workspace containing a configured manifest

    :param tmpdir: Directory where to create repo (provided by pytest automatically)
    :return: tuple of (repo object, path to workspace)
    """
    commits, source_repo = helpers.create_commits(tmpdir / "source")
    workspace = tmpdir / "workspace"
    workspace.mkdir()

    helpers.create_manifest(workspace, {"repos": [{"uri": str(tmpdir / "source/.git"), "path": "test"}]})
    os.chdir(str(workspace))

    return {"source_repo": source_repo, "workspace": workspace, "commits": commits, "tmpdir": tmpdir}


@pytest.fixture(name="synced_repo_and_workspace")
def fixture_synced_repo_and_workspace(test_repo_and_workspace):
    """
    Builds upon 'test_repo_and_workspace' and also performs an initial sync
    :param test_repo_and_workspace:
    :return: (destination repo object, source repo object, path to workspace)
    """
    data = test_repo_and_workspace
    result = CliRunner().invoke(metarepo.cli.cli, ["sync"])
    assert result.exit_code == 0

    data["dest_repo"] = git.Repo(data["workspace"] / "test")
    return data


def test_sync_basic(test_repo_and_workspace):
    """Sync nonexistant repository"""
    data = test_repo_and_workspace

    runner = CliRunner()
    result = runner.invoke(metarepo.cli.cli, ["sync"])
    assert "Checked out master" in result.output
    assert result.exit_code == 0

    # Repo is created and is in sync
    dest_repo = git.Repo(data["workspace"] / "test")
    assert dest_repo.head.commit == data["source_repo"].head.commit

    # Add additional commits
    new_commit = helpers.write_and_commit(data["source_repo"], "newfile.txt")

    # Repo no longer in sync
    previous_commit = dest_repo.head.commit
    assert previous_commit != new_commit

    # Sync
    result = runner.invoke(metarepo.cli.cli, ["sync"])
    assert result.exit_code == 0

    # Current commit has been updated
    assert dest_repo.head.commit == new_commit

    # Output mentions the updated commit
    assert str(previous_commit)[0:7] in result.output
    assert str(new_commit)[0:7] in result.output


def test_sync_no_change(synced_repo_and_workspace):
    """Syncing when no change is necessary"""
    runner = CliRunner()
    result = runner.invoke(metarepo.cli.cli, ["sync"])
    assert "Already up to date" in result.output


def test_sync_dirty(synced_repo_and_workspace):
    """If repository is dirty, sync should stop"""
    data = synced_repo_and_workspace

    # Edit file in workspace
    (data["workspace"] / "test" / "output.txt").write(u"Changed")

    result = CliRunner().invoke(metarepo.cli.cli, ["sync"])
    assert result.exit_code == 1


def test_sync_ahead(synced_repo_and_workspace):
    """If repository is ahead origin sync should stop"""
    data = synced_repo_and_workspace

    # Commit file in workspace
    helpers.write_and_commit(data["dest_repo"], "output.txt")

    result = CliRunner().invoke(metarepo.cli.cli, ["sync"])
    assert result.exit_code == 1


def test_sync_different_branch(synced_repo_and_workspace):
    """If we have a different branch checked out than the tracked branch we
    should switch to the correct branch even if it is behind"""
    data = synced_repo_and_workspace

    # Create a branch in the source repo that is behind master
    data["source_repo"].create_head("my_branch", data["commits"][5])

    # Modify manifest to track the new branch
    helpers.create_manifest(
        data["workspace"],
        {"repos": [{"uri": str(data["tmpdir"] / "source/.git"), "path": "test", "track": "my_branch"}]},
    )

    # We are currently master
    assert data["dest_repo"].head.commit == data["commits"][0]
    assert data["dest_repo"].active_branch.name == "master"

    # Sync repo
    result = CliRunner().invoke(metarepo.cli.cli, ["sync"])
    print(result.output)
    assert result.exit_code == 0

    # We expect to be at the tracked branch now
    assert data["dest_repo"].head.commit == data["commits"][5]
    assert data["dest_repo"].active_branch.name == "my_branch"
