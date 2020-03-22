"""Manifest loading"""
import yaml
import os
import cfgv

from pathlib import Path
from typing import Any, Union, List


class ManifestError(Exception):
    """Basic error"""


class ValidationFailed(ManifestError):
    """Validation of manifest failed"""

    def __init__(self, e: cfgv.ValidationError):
        super().__init__(str(e))


class NotFound(ManifestError):
    """Manifest was not found"""


# Schema for repository
REPO_SCHEMA = cfgv.Map(
    "Repo",
    "uri",
    cfgv.Required("uri", cfgv.check_string),
    cfgv.Required("path", cfgv.check_string),
)

# Schema for manifest
MANIFEST_SCHEMA = cfgv.Map(
    "Manifest",
    None,
    cfgv.RequiredRecurse("repos", cfgv.Array(REPO_SCHEMA, allow_empty=False)),
)


class Repository:
    """Data for one repository"""

    def __init__(self, uri: str, path: Union[os.PathLike, str]):
        self._uri = uri
        self._path = Path(path)

    @property
    def uri(self):
        """
        :return: URI to repository
        """
        return self._uri

    @property
    def path(self) -> Path:
        """
        :return: Path to repository on disk
        """
        return self._path


class Manifest:
    """Manifest data"""

    def __init__(self, data: dict):
        self._repos = []

        for repo in data["repos"]:
            self._repos.append(Repository(**repo))

    def get_repos(self) -> List[Repository]:
        return self._repos


def load_manifest(path: Union[Path, str]) -> Manifest:
    """
    Load manifest from a file
    :param path: Path to file
    :return: Manifest
    """
    try:
        with open(path, "r") as fp:
            return parse_manifest(yaml.load(fp, yaml.SafeLoader))
    except FileNotFoundError:
        raise NotFound()


def parse_manifest(data: Any) -> Manifest:
    """Validate data and construct a Manifest
    :param data: Manifest data to be validated
    :return: Manifest
    """
    try:
        manifest_data = cfgv.validate(data, MANIFEST_SCHEMA)
        return Manifest(manifest_data)
    except cfgv.ValidationError as e:
        raise ValidationFailed(e)
