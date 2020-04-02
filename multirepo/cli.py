"""Command line interface"""
from pathlib import Path
import click
from multirepo.manifest import load_manifest
from multirepo import vcs_git


@click.group()
def cli():
    """Base CLI group"""


@cli.command()
def info():
    """List all configured meta repositories"""
    manifest = load_manifest("manifest.yml")
    for repo in manifest.get_repos():
        click.echo(f"repo: {repo.path} -> {repo.uri}")


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

    for repo_data in repos:
        try:
            repo = vcs_git.RepoTool(root_path / repo_data.path, repo_data.uri)
            repo_status = repo.get_status()
            current_head = (
                repo_status.active_branch.name
                if repo_status.active_branch
                else repo_status.head.hexsha[0:8]
            )

            click.echo(
                f"{str(repo_data.path):<30} {current_head:<20} dirty:{repo_status.is_dirty}"
            )
        except vcs_git.NotFound:
            click.echo(f"{str(repo_data.path):<30} E:NOT FOUND")
        except vcs_git.InvalidRepository:
            click.echo(f"{str(repo_data.path):<30} E:INVALID")
        except vcs_git.WrongOrigin:
            click.echo(f"{str(repo_data.path):<30} E:ORIGIN MISMATCH")


if __name__ == "__main__":
    cli()
