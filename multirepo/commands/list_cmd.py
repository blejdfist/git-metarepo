"""List repositories command"""
import click
from multirepo.manifest import load_manifest
import multirepo.ui as ui


@click.command(name="list")
def list_repos():
    """List all configured meta repositories"""
    manifest = load_manifest("manifest.yml")
    repos = manifest.get_repos()

    ui.info(f"Listing {len(repos)} configured repositories")

    for repo in manifest.get_repos():
        ui.item(f"{repo.path}", ("uri", repo.uri))
