from hackintosh import ALL_META
from hackintosh.lib import execute_func, cleanup

import click, os


@click.command(short_help='Prepare all stuff for device.')
@click.option('-p', '--patch', required=True, type=click.Choice(ALL_META['patches'].keys()),
              help='Choose the laptop series')
def cli(patch):
    cleanup()
    execute_func(os.path.basename(__file__)[:5], patch)


