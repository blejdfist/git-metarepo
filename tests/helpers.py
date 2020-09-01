"""Test helpers"""
import os
import pathlib

import git
import yaml
from metarepo import manifest


def create_commits(path, origin_uri=None):
    """
    Creates a test repository with a bunch of commits
    :param path: Path where the repository should be created
    :param origin_uri: URI to origin
    :return: (List of commits, Repo)
    """
    # Create repository
    repo = git.Repo.init(path)

    if origin_uri:
        repo.create_remote("origin", origin_uri)

    commits = []
    for i in range(0, 10):
        filename = os.path.join(path, "output.txt")
        with open(filename, "a+") as output_file:
            output_file.write(f"This is a test {i}\n")

        repo.index.add([filename])
        commits.insert(0, repo.index.commit(f"Commit message {i}"))

    return commits, repo


def create_manifest(tmpdir, data):
    """
    Write the manifest to a file
    :param tmpdir: tmpdir from pytest
    :param data: Manifest data
    """
    tmpdir.join(manifest.MANIFEST_NAME).write(yaml.dump(data))


def write_and_commit(repo, filename):
    full_path = pathlib.Path(repo.working_dir) / filename
    full_path.write_text(f"Editing {filename}")

    repo.index.add([filename])
    return repo.index.commit(f"Wrote to {filename}")
