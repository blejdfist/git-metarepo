import git
import pytest
from metarepo.vcs_git import InvalidRepository, RepoTool
from tests import helpers


def test_invalid_repository(tmpdir):
    with pytest.raises(InvalidRepository):
        RepoTool(tmpdir)


def test_root_path(test_repo_and_workspace):
    repo_path = test_repo_and_workspace["workspace"] / "repo"
    source_repo = test_repo_and_workspace["source_repo"]

    repo = RepoTool(repo_path, expected_origin=source_repo.git_dir, allow_create=True)
    assert repo.get_root_path() == repo_path


def test_fetch_behind(test_repo_and_workspace):
    """If updates are made on the remote, we will be behind locally"""
    data = test_repo_and_workspace

    repo = RepoTool(data["workspace"] / "repo", expected_origin=data["source_repo"].git_dir, allow_create=True)

    # Fetch and checkout to make sure we have a local head
    fetch_result = repo.fetch("master")
    repo.checkout("origin/master", "master")

    # We are currently up to date
    assert fetch_result.ahead == []
    assert fetch_result.behind == []

    new_commit = helpers.write_and_commit(data["source_repo"], "new_file_on_remote")

    # Fetch the new commit
    fetch_result = repo.fetch("master")

    # We are now behind
    assert fetch_result.ahead == []
    assert fetch_result.behind == [new_commit]


def test_fetch_ahead(test_repo_and_workspace):
    """If updates are made on locally, we will be ahead locally"""
    data = test_repo_and_workspace

    repo = RepoTool(data["workspace"] / "repo", expected_origin=data["source_repo"].git_dir, allow_create=True)

    # Fetch and checkout to make sure we have a local head
    repo.fetch("master")
    repo.checkout("origin/master", "master")

    new_commit = helpers.write_and_commit(git.Repo(data["workspace"] / "repo"), "new_file_created_locally")

    # Fetch the new commit
    fetch_result = repo.fetch("master")

    # We are now behind
    assert fetch_result.ahead == [new_commit]
    assert fetch_result.behind == []


def test_checkout(test_repo_and_workspace):
    data = test_repo_and_workspace

    repo = RepoTool(data["workspace"] / "repo", expected_origin=data["source_repo"].git_dir, allow_create=True)
    repo.fetch("master")
    repo.checkout("origin/master", "master")

    new_commit = helpers.write_and_commit(data["source_repo"], "new_file_on_remote")

    # Fetch the new commit
    repo.fetch("master")
    repo.checkout("origin/master", "master")

    status = repo.get_status()
    assert status.untracked_files == []
    assert not status.is_dirty
    assert status.head == new_commit


def test_local_is_dirty(test_repo_and_workspace_behind):
    """When local files are modified, the repository is considered dirty"""
    data = test_repo_and_workspace_behind

    repo = RepoTool(data["workspace"], expected_origin=data["source_repo"].git_dir, allow_create=True)
    status = repo.get_status()
    assert not status.is_dirty
    assert status.head == data["commits"][0]

    # Modify one of the files
    output = data["workspace"] / "output.txt"
    output.write("New content")

    # Repo should be dirty now
    status = repo.get_status()
    assert status.is_dirty
