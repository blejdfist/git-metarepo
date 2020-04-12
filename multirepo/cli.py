"""Command line interface"""
import click
from .commands.status_cmd import status
from .commands.list_cmd import list_repos
from .commands.sync_cmd import sync


@click.group()
def cli():
    """Base CLI group"""


# Register commands
cli.add_command(status)
cli.add_command(list_repos)
cli.add_command(sync)

if __name__ == "__main__":
    cli()  # pragma: no cover
