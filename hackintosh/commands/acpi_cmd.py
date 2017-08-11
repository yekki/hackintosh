from hackintosh import LAPTOP_META
from hackintosh.lib import cleanup, execute_module
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
    click.echo(click.style('SSDT List:', fg='blue'))
    click.echo(click.style(', '.join(LAPTOP_META['acpi']['patches']['ssdt_list']), fg='green'))

    for k in LAPTOP_META['acpi']['patches']['ssdt'].keys():
        click.echo(click.style(f"{k.upper()} Patches:", fg='blue'))
        click.echo(click.style(', '.join(LAPTOP_META['acpi']['patches']['ssdt'][k]), fg='green'))

    click.echo(click.style('DSDT Patches:', fg='blue'))
    click.echo(click.style(', '.join(LAPTOP_META['acpi']['patches']['dsdt']), fg='green'))