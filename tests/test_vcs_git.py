"""Test vcs_git module"""
import pytest
import git
from metarepo import vcs_git
from tests import helpers

REPO_URI = "git://127.0.0.1/repo"


def test_git_status_invalid(tmpdir):
    """Folder exists but is not a valid git repository"""
    with pytest.raises(vcs_git.InvalidRepository):
        vcs_git.RepoTool(tmpdir, REPO_URI)


def test_git_status_nonexistant(tmpdir):
    """Folder does not exist"""
    with pytest.raises(vcs_git.NotFound):
        vcs_git.RepoTool(tmpdir.join("repo"), REPO_URI)


def test_git_status_wrong_origin(tmpdir):
    """Repo exists but has a different origin than expected"""
    # Create repository
    repo = git.Repo.init(tmpdir)
    repo.create_remote("origin", "git://127.0.0.1/wrongrepo")

    with pytest.raises(vcs_git.WrongOrigin):
        vcs_git.RepoTool(tmpdir, REPO_URI)


def test_git_status_no_origin(tmpdir):
    """Repo exists but has a different origin than expected"""
    # Create repository
    git.Repo.init(tmpdir)

    with pytest.raises(vcs_git.WrongOrigin):
        vcs_git.RepoTool(tmpdir, REPO_URI)


def test_git_status(tmpdir):
    """Check status of a clean repository"""
    commits, _ = helpers.create_commits(tmpdir, REPO_URI)

    repo = vcs_git.RepoTool(tmpdir, REPO_URI)
    status = repo.get_status()

    assert not status.is_dirty
    assert not status.is_detached
    assert status.active_branch.name == "master"
    assert status.head == commits[0]
    assert status.untracked_files == []


def test_git_status_dirty(tmpdir):
    """Check status of a repository with modified files"""
    commits, _ = helpers.create_commits(tmpdir, REPO_URI)
    tmpdir.join("output.txt").write("Edit")

    repo = vcs_git.RepoTool(tmpdir, REPO_URI)
    status = repo.get_status()

    assert status.is_dirty
    assert not status.is_detached
    assert status.active_branch.name == "master"
    assert status.head == commits[0]
    assert status.untracked_files == []


def test_git_status_detached_head(tmpdir):
    """Check status of a repository with a detached head"""
    commits, test_repo = helpers.create_commits(tmpdir, REPO_URI)

    test_repo.git.checkout(commits[3])

    repo = vcs_git.RepoTool(tmpdir, REPO_URI)
    status = repo.get_status()

    assert not status.is_dirty
    assert status.is_detached
    assert status.active_branch is None
    assert status.head == commits[3]
    assert status.untracked_files == []


def test_git_detect_root(tmpdir):
    """Get the root of the repository"""
    helpers.create_commits(tmpdir, REPO_URI)

    tmpdir.mkdir("a").mkdir("b").mkdir("c")
    repo = vcs_git.RepoTool(tmpdir.join("a/b/c"), REPO_URI, search_parent=True)

    assert repo.get_root_path() == tmpdir
