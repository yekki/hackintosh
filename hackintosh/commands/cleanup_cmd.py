from hackintosh.lib import cleanup
import click


@click.command(short_help='Clean current working directory.')
def cli():
    cleanup()
    click.clear()

