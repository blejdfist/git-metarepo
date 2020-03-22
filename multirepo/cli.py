import click


@click.group()
def cli():
    pass


@cli.command()
def info():
    pass


if __name__ == "__main__":
    cli()
