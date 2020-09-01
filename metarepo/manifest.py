"""Manifest loading"""
from pathlib import Path
from typing import Any, List, Optional, Union

import pydantic
import yaml

# Manifest filename
MANIFEST_NAME = "manifest.yml"


class ManifestError(Exception):
    """Basic error"""


class ValidationFailed(ManifestError):
    """Validation of manifest failed"""

    def __init__(self, e: pydantic.ValidationError):
        super().__init__(str(e))


class NotFound(ManifestError):
    """Manifest was not found"""


class Repository(pydantic.BaseModel):
    """Data for one repository"""

    url: str
    path: Path
    track: Optional[str] = "master"


class Manifest(pydantic.BaseModel):
    """Manifest data"""

    repos: pydantic.conlist(Repository, min_items=1)

    def get_repos(self) -> List[Repository]:
        return self.repos


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
        return Manifest(**data)
    except pydantic.ValidationError as exception:
        raise ValidationFailed(exception)
