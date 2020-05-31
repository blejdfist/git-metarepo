"""Status command"""
import sys
from pathlib import Path

import click
import git
from metarepo import ui, vcs_git
from metarepo.cli_decorators import require_manifest
from metarepo.manifest import Manifest, Repository


def do_sync_repo(repo_path: Path, repo_data: Repository):
    """
    Perform synchronization of one repository
    :param repo_path: Path to repository
    :param repo_data: Repository data
    :return: True if successful
    """
    ui.item(str(repo_data.path), ("track", repo_data.track))
    if not repo_path.exists():
        repo = git.Repo.init(repo_path)
        repo.create_remote("origin", repo_data.uri)

    repo = vcs_git.RepoTool(repo_path, repo_data.uri)

    # Fetch
    fetch_result = repo.fetch(repo_data.track)

    # Warn if ahead
    if fetch_result.ahead:
        ui.item_error(f"Skipped {str(repo_data.path)}", err=f"Ahead by {len(fetch_result.ahead)} commit(s)")
        return False

    status = repo.get_status()

    # Warn if dirty
    if status.is_dirty:
        ui.item_error(f"Skipped {str(repo_data.path)}", err="Workspace is dirty")
        return False

    current_commit = status.head
    new_commit = fetch_result.fetch_head

    extras = []

    if current_commit is None:
        extras.append(f"Checked out {repo_data.track}")
    elif current_commit == new_commit:
        extras.append(f"Already up to date")
    else:
        extras.append(("update", f"{str(current_commit)[0:7]} -> {str(new_commit)[0:7]}"))
        extras.append(("commits", len(fetch_result.behind)))

    repo.checkout("origin/" + repo_data.track, repo_data.track)
    ui.item_ok(str(repo_data.path), *extras)

    return True


@click.command()
@require_manifest
def sync(manifest: Manifest, root_path: str):
    """Synchronize all configured repositories"""
    repos = manifest.get_repos()

    ui.info(f"Synchronizing {len(repos)} repositories")

    # Determine which repositories are candidates for syncing
    for repo_data in repos:
        repo_path = root_path / repo_data.path
        if not do_sync_repo(repo_path, repo_data):
            sys.exit(1)
