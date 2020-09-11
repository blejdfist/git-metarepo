"""Status command"""
import concurrent.futures
import sys
from pathlib import Path

import click
import git
from metarepo import ui, vcs_git
from metarepo.cli_decorators import require_manifest
from metarepo.manifest import Manifest, Repository
from prompt_toolkit import ANSI
from prompt_toolkit.shortcuts.progress_bar import ProgressBar, formatters


def do_sync_repo(progress: ProgressBar, repo_path: Path, repo_data: Repository):
    """
    Perform synchronization of one repository
    :param progress: ProgressBar instance
    :param repo_path: Path to repository
    :param repo_data: Repository data
    :return: True if successful
    """
    pb = progress()
    pb.label = ANSI(ui.format_item(str(repo_data.path), ("track", repo_data.track)))

    if not repo_path.exists():
        repo = git.Repo.init(repo_path)
        repo.create_remote("origin", repo_data.url)

    try:
        repo = vcs_git.RepoTool(repo_path, repo_data.url)
    except vcs_git.InvalidRepository:
        pb.label = ANSI(ui.format_item_error(f"Unable to open {repo_data.path!s}", "Invalid repository"))
        return False

    # Fetch
    fetch_result = repo.fetch(repo_data.track)

    # Warn if ahead
    if fetch_result.ahead:
        pb.label = ANSI(
            ui.format_item_error(f"Skipped {repo_data.path!s}", err=f"Ahead by {len(fetch_result.ahead)} commit(s)")
        )
        return False

    status = repo.get_status()

    # Warn if dirty
    if status.is_dirty:
        pb.label = ANSI(ui.format_item_error(f"Skipped {repo_data.path!s}", err="Workspace is dirty"))
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
    pb.label = ANSI(ui.format_item_ok(str(repo_data.path), *extras))

    return True


@click.command()
@click.option(
    "-j", "--parallel", type=int, default=1, show_default=True, help="Number of repositories to synchronize in parallel"
)
@require_manifest
def sync(manifest: Manifest, root_path: str, parallel: int):
    """Synchronize all configured repositories"""
    repos = manifest.get_repos()

    title = ANSI(ui.format_info(f"Synchronizing {len(repos)} repositories"))

    progress_formatter = [
        formatters.Label(),
    ]

    # Synchronize all repositories
    with ProgressBar(title, formatters=progress_formatter) as progress_bar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as thread_pool:
            tasks = [thread_pool.submit(do_sync_repo, progress_bar, root_path / repo.path, repo) for repo in repos]
            for future in concurrent.futures.as_completed(tasks):
                if not future.result():
                    sys.exit(1)
