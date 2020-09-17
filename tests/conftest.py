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

    helpers.create_manifest(workspace, {"repos": [{"url": str(tmpdir / "source" / ".git"), "path": "test"}]})
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
