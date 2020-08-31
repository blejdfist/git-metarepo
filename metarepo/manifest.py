"""Manifest loading"""
import os
from pathlib import Path
from typing import Any, List, Union

import cfgv
import yaml


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
    "url",
    cfgv.Required("url", cfgv.check_string),
    cfgv.Required("path", cfgv.check_string),
    cfgv.Optional("track", cfgv.check_string, default="master"),
)

# Schema for manifest
MANIFEST_SCHEMA = cfgv.Map("Manifest", None, cfgv.RequiredRecurse("repos", cfgv.Array(REPO_SCHEMA, allow_empty=False)),)


class Repository:
    """Data for one repository"""

    def __init__(self, url: str, path: Union[os.PathLike, str], track: str):
        self._url = url
        self._path = Path(path)
        self._track = track

    @property
    def url(self):
        """
        :return: URI to repository
        """
        return self._url

    @property
    def path(self) -> Path:
        """
        :return: Path to repository on disk
        """
        return self._path

    @property
    def track(self) -> str:
        """
        :return: Tracked revision
        """
        return self._track


class Manifest:
    """Manifest data"""

    def __init__(self, data: dict):
        """
        Construct manifest
        :param data:
        """
        self._repos = []

        for repo in data["repos"]:
            self._repos.append(Repository(**repo))

    def get_repos(self) -> List[Repository]:
        """
        :return: List of repositories in the manifest
        """
        return self._repos


def load_manifest(path: Union[Path, str]) -> Manifest:
    """
    Load manifest from a file
    :param path: Path to file
    :return: Manifest
    """
    try:
        with open(path, "r") as manifest_file:
            return parse_manifest(yaml.load(manifest_file, yaml.SafeLoader))
    except FileNotFoundError:
        raise NotFound()


def parse_manifest(data: Any) -> Manifest:
    """Validate data and construct a Manifest
    :param data: Manifest data to be validated
    :return: Manifest
    """
    try:
        manifest_data = cfgv.validate(data, MANIFEST_SCHEMA)
        return Manifest(cfgv.apply_defaults(manifest_data, MANIFEST_SCHEMA))
    except cfgv.ValidationError as exception:
        raise ValidationFailed(exception)
