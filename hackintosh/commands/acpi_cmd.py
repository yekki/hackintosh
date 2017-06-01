from hackintosh import *


@click.group()
def cli():
    pass


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
