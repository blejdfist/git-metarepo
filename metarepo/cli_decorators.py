"""CLI decorators"""
import functools
import sys
from pathlib import Path

from . import manifest, ui, vcs_git


def require_manifest(func):
    """Pass the parsed manifest and the workspace root as the first two arguments"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Assume the manifest is in the current directory
        try:
            # If we are in a repository, we want to look in
            # the root of that repository for the manifest
            current_repo = vcs_git.RepoTool(Path.cwd(), search_parent=True)
            root_path = current_repo.get_root_path()
        except vcs_git.InvalidRepository:
            # Since we are not in a repository we will look
            # for the manifest in the current directory
            root_path = Path.cwd()

        manifest_path = root_path / manifest.MANIFEST_NAME

        try:
            loaded_manifest = manifest.load_manifest(manifest_path)
            return func(loaded_manifest, root_path, *args, **kwargs)
        except manifest.NotFound:
            ui.error(f"Unable to load manifest: Not found: {str(manifest_path)}")
            sys.exit(1)
        except manifest.ValidationFailed as exc:
            ui.error(f"Unable to load manifest: Validation failed")
            ui.error(str(exc))
            sys.exit(1)

    return wrapper
