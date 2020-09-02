"""Command for creating a manifest file"""
import sys
from pathlib import Path

import click
import prompt_toolkit
from metarepo import manifest, ui, vcs_git
from prompt_toolkit.completion.filesystem import PathCompleter
from prompt_toolkit.validation import Validator


@click.command()
def init():
    """Creates a manifest file in the root of the repository or the current directory"""
    try:
        current_repo = vcs_git.RepoTool(Path.cwd(), search_parent=True)
        root_path = current_repo.get_root_path()
    except vcs_git.InvalidRepository:
        root_path = Path.cwd()

    manifest_file = root_path / manifest.MANIFEST_NAME

    if manifest_file.exists():
        ui.error(f"A {manifest.MANIFEST_NAME} file already exists")
        sys.exit(1)

    ui.info(f"Using manifest path {manifest_file!s}")

    validate_not_empty = Validator.from_callable(lambda c: len(c) > 0)

    repos = []

    session = prompt_toolkit.PromptSession(validator=validate_not_empty)
    done = False
    while not done:
        ui.info("Adding repository to the manifest")
        url = session.prompt("URL of repository: ")
        path = session.prompt("Path to clone repository to: ", completer=PathCompleter(only_directories=True))
        track = session.prompt("Track: ", default="master")
        repos.append(manifest.Repository(url=url, path=path, track=track))

        done = not prompt_toolkit.shortcuts.confirm("Add another repository?")

    new_manifest = manifest.Manifest(repos=repos)
    try:
        manifest.save_manifest(new_manifest, manifest_file)
        ui.item_ok(f"Saved manifest to {manifest_file!s}")
    except Exception as exc:
        ui.error(f"Failed to save manifest: {exc!s}")
