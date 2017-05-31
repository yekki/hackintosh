from hackintosh.utils import cleanup, delete_file, Path

import click


@click.command()
def cli():
    cleanup()
    click.clear()
