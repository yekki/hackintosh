from hackintosh import *
from hackintosh.commands import execute_module, cleanup

import click, pprint


@click.group()
@click.option('-s', '--series', default=SUPPORTED_SERIES[0], required=True, type=click.Choice(SUPPORTED_SERIES),
              help='Choose your laptop series.')
@pass_context
def cli(ctx, series):
    ctx.series = series


@cli.command(short_help='Build & patch ACPI files.')
@pass_context
def build(ctx):
    cleanup()
    execute_module('acpi', ctx)


@cli.command(short_help='Show ACPI patches in json format.')
@pass_context
def info(ctx):
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(ctx.laptop)
