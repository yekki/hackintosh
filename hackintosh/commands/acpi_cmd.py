from hackintosh import LAPTOP_META
from hackintosh.lib import cleanup, execute_module
import click, pprint

@click.group(short_help="Commands for patching & building DSDT/SSDT(s)")
def cli():
    pass


@cli.command(short_help='Build & patch ACPI files')
def build():
    cleanup()
    execute_module('acpi')


@cli.command(short_help='Show ACPI patches in json format')
def info():
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(LAPTOP_META)
