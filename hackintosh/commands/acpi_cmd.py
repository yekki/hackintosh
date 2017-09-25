from hackintosh import LAPTOP_META
from hackintosh.lib import cleanup, execute_module, message
import click


@click.group(short_help="Commands for patching & building DSDT/SSDT(s).")
def cli():
    pass


@cli.command(short_help='Build & patch ACPI files.')
def build():
    cleanup()
    execute_module('acpi')


@cli.command(short_help='Show ACPI patches in json format.')
def info():
    message('SSDT List:')
    message(', '.join(LAPTOP_META['acpi']['patches']['ssdt_list']), fg='green', nl=True)

    for k in LAPTOP_META['acpi']['patches']['ssdt'].keys():
        message(f"{k.upper()} Patches:")
        message(', '.join(LAPTOP_META['acpi']['patches']['ssdt'][k]), fg='green', nl=True)

    message('DSDT Patches:')
    message(', '.join(LAPTOP_META['acpi']['patches']['dsdt']), fg='green')
