"""GIT Utilities"""
import configparser
import os.path
from collections import namedtuple
from pathlib import Path
from typing import Union

import git


class GitError(Exception):
    """Error base class"""


class NotFound(GitError):
    """Path was not found"""


class WrongOrigin(GitError):
    """Path was a repository, but the repository did not have the expected origin"""

    def __init__(self, urls=None):
        if urls is None:
            urls = []
        super().__init__("\n".join(urls))


class InvalidRepository(GitError):
    """Path exists but was not a git repository"""


RepoStatus = namedtuple("RepoStatus", ["active_branch", "untracked_files", "head", "is_detached", "is_dirty"])
FetchResult = namedtuple("FetchResult", ["fetch_head", "ahead", "behind"])


class RepoTool:
    """Repository management tool"""

    def __init__(self, path: Union[Path, str], expected_origin=None, search_parent=False):
        """
        Repository tool
        :param path: Path to git repository
        :param expected_origin: Expected origin
        :param search_parent: Recursively search parent for repository
        """
        try:
            self._repo = git.Repo(path=path, search_parent_directories=search_parent)
        except git.InvalidGitRepositoryError:
            raise InvalidRepository()
        except git.NoSuchPathError:
            raise NotFound()

        # Validate origin if provided
        if expected_origin:
            try:
                origin = self._repo.remote("origin")
            except (ValueError, configparser.NoSectionError):
                raise WrongOrigin()

            origin_urls = list(origin.urls)
            if expected_origin not in origin_urls:
                # Git on Windows can give paths with mixed slashes
                # when using local file paths as repos
                if expected_origin not in [os.path.normpath(url) for url in origin_urls]:
                    raise WrongOrigin(origin_urls)

        self._path = Path(self._repo.working_tree_dir)

    def get_status(self) -> RepoStatus:
        """Retrieve the status of the repository"""

        info = {
            "is_detached": self._repo.head.is_detached,
            "is_dirty": self._repo.is_dirty(),
            "untracked_files": self._repo.untracked_files,
            "head": self._repo.head.commit if self._repo.heads else None,
        }

        if info["is_detached"]:
            info["active_branch"] = None
        else:
            info["active_branch"] = self._repo.active_branch

        return RepoStatus(**info)

    def get_root_path(self) -> Path:
        """Get the root path of the current git repository"""
        return self._path

    def fetch(self, ref, progress_cb=None) -> FetchResult:
        """
        Fetch ref
        :param ref: Reference to fetch
        :param progress_cb: Callback to call with progress
        :return: Dictionary with the fetch result
        """
        fetch_result = self._repo.remote("origin").fetch(ref, progress=progress_cb)

        result = {"fetch_head": fetch_result[0].commit, "ahead": [], "behind": []}

        # If we have anything checked out locally
        # Retrieve which commits are ahead or behind the remote
        if ref in self._repo.heads:
            local_ref = str(self._repo.heads[ref])
            remote_ref = str(result["fetch_head"])
            result["ahead"] = list(self._repo.iter_commits(f"{remote_ref}..{local_ref}"))
            result["behind"] = list(self._repo.iter_commits(f"{local_ref}..{remote_ref}"))

        return FetchResult(**result)

    def checkout(self, ref, name, track=None):
        """
        Checkout a ref into the local workspace
        :param ref: Ref to checkout
        :param name: Name of head to create if it doesn't exist
        :param track: What remote branch to track (if any)
        """
        if name not in self._repo.heads:
            self._repo.create_head(name, ref)
        else:
            self._repo.heads[name].set_commit(ref)

        self._repo.heads[name].checkout()
        # self._repo.head.reset(index=True, working_tree=True)

        if track:
            self._repo.heads[name].set_tracking_branch(track)
