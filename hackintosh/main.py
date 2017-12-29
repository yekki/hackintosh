from hackintosh import CLIENT_SETTINGS
from hackintosh.cli import MainCLI
import click

@click.command(cls=MainCLI, context_settings=CLIENT_SETTINGS['context_settings'])
def cli():
    pass