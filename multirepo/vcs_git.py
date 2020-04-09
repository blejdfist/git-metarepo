"""GIT Utilities"""
from typing import Union
from collections import namedtuple
from pathlib import Path
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


RepoStatus = namedtuple("RepoStatus", ["active_branch", "untracked_files", "head", "is_detached", "is_dirty"],)


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
            except ValueError:
                raise WrongOrigin()

            origin_urls = list(origin.urls)
            if expected_origin not in origin_urls:
                raise WrongOrigin(origin_urls)

        self._path = Path(self._repo.working_tree_dir)

    def get_status(self) -> RepoStatus:
        """Retrieve the status of the repository"""

        info = {
            "is_detached": self._repo.head.is_detached,
            "is_dirty": self._repo.is_dirty(),
            "untracked_files": self._repo.untracked_files,
            "head": self._repo.head.commit,
        }

        if info["is_detached"]:
            info["active_branch"] = None
        else:
            info["active_branch"] = self._repo.active_branch

        return RepoStatus(**info)

    def get_root_path(self) -> Path:
        """Get the root path of the current git repository"""
        return self._path
