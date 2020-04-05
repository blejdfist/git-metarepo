"""Command line interface"""
from pathlib import Path
import click
from multirepo.manifest import load_manifest
from multirepo import vcs_git
import multirepo.ui as ui


@click.group()
def cli():
    """Base CLI group"""


@cli.command(name="list")
def list_repos():
    """List all configured meta repositories"""
    manifest = load_manifest("manifest.yml")
    repos = manifest.get_repos()

    ui.info(f"Listing {len(repos)} configured repositories")

    for repo in manifest.get_repos():
        ui.item(f"{repo.path}", ("uri", repo.uri))


@cli.command()
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


if __name__ == "__main__":
    cli()
