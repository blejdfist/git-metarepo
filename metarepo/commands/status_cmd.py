"""Status command"""
import click
from metarepo import ui, vcs_git
from metarepo.cli_decorators import require_manifest


@click.command()
@require_manifest
def status(manifest, root_path):
    """Show the status of all configured repositories"""
    repos = manifest.get_repos()

    ui.info(f"Checking status for {len(repos)} repositories")

    for repo_data in repos:
        repo_path = str(repo_data.path)

        try:
            repo = vcs_git.RepoTool(root_path / repo_data.path, repo_data.url)
            repo_status = repo.get_status()
            current_head = repo_status.active_branch.name if repo_status.active_branch else repo_status.head.hexsha[0:8]

            ui.item_ok(repo_path, ("track", repo_data.track), ("head", current_head), ("dirty", repo_status.is_dirty))
        except vcs_git.NotFound:
            ui.item_error(repo_path, "NOT FOUND")
        except vcs_git.InvalidRepository:
            ui.item_error(repo_path, "INVALID")
        except vcs_git.WrongOrigin:
            ui.item_error(repo_path, "ORIGIN MISMATCH")
