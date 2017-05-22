from hackintosh.main import pass_context
from hackintosh.utils import execute

import click, pprint


@click.group()
@click.option('-s', '--series', default='z30-b', required=True, type=click.Choice(['t440-p', 'z30-b']), help='Choose your laptop series.')
@pass_context
def cli(ctx, series):
    ctx.series = series


@cli.command(short_help='Build & patch ACPI files.')
@pass_context
def build(ctx):
    execute(ctx, 'acpi')


@cli.command(short_help='Show ACPI patches in json format.')
@pass_context
def show(ctx):
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(ctx.laptop)