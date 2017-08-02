from hackintosh.lib import cleanup
import click


@click.command()
def cli():
    cleanup()
    click.clear()
