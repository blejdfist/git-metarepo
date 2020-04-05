"""Command line interface"""
import click
from .commands.status_cmd import status
from .commands.list_cmd import list_repos


@click.group()
def cli():
    """Base CLI group"""


# Register commands
cli.add_command(status)
cli.add_command(list_repos)

if __name__ == "__main__":
    cli()
