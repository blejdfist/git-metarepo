import click
from multirepo.manifest import load_manifest


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--filename",
    "-f",
    type=click.Path(exists=True),
    show_default=True,
    default="manifest.yml",
)
def info(filename):
    manifest = load_manifest(filename)
    for repo in manifest.get_repos():
        click.echo(f"repo: {repo.path} -> {repo.uri}")


if __name__ == "__main__":
    cli()
