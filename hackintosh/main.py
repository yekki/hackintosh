from hackintosh import CLIENT_SETTINGS
from hackintosh.cli import MainCLI
import click


# pass_context = click.make_pass_decorator(Context, ensure=True)

@click.command(cls=MainCLI, context_settings=CLIENT_SETTINGS['context_settings'])
def cli():
    pass
