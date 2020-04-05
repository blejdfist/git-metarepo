"""Status command"""
from pathlib import Path
import click

from multirepo.manifest import load_manifest
import multirepo.ui as ui
import multirepo.vcs_git as vcs_git


@click.command()
def status():
    """Show the status of all meta repositories"""
    root_path = Path.cwd()

    try:
        # If we are in a repository, we want to look in
        # the root of that repository for the manifest
        main_repo = vcs_git.RepoTool(root_path)
        root_path = main_repo.get_root_path()
    except vcs_git.InvalidRepository:
        pass

    manifest = load_manifest(root_path / "manifest.yml")
    repos = manifest.get_repos()

    ui.info(f"Checking status for {len(repos)} repositories")

    for repo_data in repos:
        repo_path = str(repo_data.path)

        try:
            repo = vcs_git.RepoTool(root_path / repo_data.path, repo_data.uri)
            repo_status = repo.get_status()
            current_head = repo_status.active_branch.name if repo_status.active_branch else repo_status.head.hexsha[0:8]

            ui.item_ok(repo_path, ("head", current_head), ("dirty", repo_status.is_dirty))
        except vcs_git.NotFound:
            ui.item_error(repo_path, "NOT FOUND")
        except vcs_git.InvalidRepository:
            ui.item_error(repo_path, "INVALID")
        except vcs_git.WrongOrigin:
            ui.item_error(repo_path, "ORIGIN MISMATCH")
