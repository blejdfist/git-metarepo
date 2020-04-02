"""Test helpers"""
import os
import git


def create_commits(path, origin_uri):
    """
    Creates a test repository with a bunch of commits
    :param path: Path where the repository should be created
    :param origin_uri: URI to origin
    :return: (List of commits, Repo)
    """
    # Create repository
    repo = git.Repo.init(path)
    repo.create_remote("origin", origin_uri)

    commits = []
    for i in range(0, 10):
        filename = os.path.join(path, "output.txt")
        with open(filename, "a+") as output_file:
            output_file.write(f"This is a test {i}\n")

        repo.index.add([filename])
        commits.insert(0, repo.index.commit(f"Commit message {i}"))

    return commits, repo
