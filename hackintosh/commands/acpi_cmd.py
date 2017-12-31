from hackintosh import LAPTOP_META, STAGE_DIR, LAPTOP_ROOT, ALL_META, PKG_ROOT, CLIENT_SETTINGS, OUTPUT_DIR, error
from hackintosh.lib import cleanup, execute_module
from subprocess import call
import click, os, shutil


_IASL = os.path.join(PKG_ROOT, 'bin', ALL_META['tools']['iasl'])


@click.group(short_help="Commands for patching & building DSDT/SSDT(s).")
def cli():
    pass


@cli.command(short_help='Build & patch ACPI files.')
@click.option('-h', '--hotpatch', is_flag=True, help='Build hotpatches')
def build(hotpatch):
    cleanup()
    if hotpatch:
        src = os.path.join(LAPTOP_ROOT, 'hotpatches')
        series = CLIENT_SETTINGS['current_series'].upper()
        for f in os.listdir(src):
            shutil.copy2(os.path.join(src, f), os.path.join(STAGE_DIR, f))
        
        os.chdir(STAGE_DIR)
        call([f'{_IASL} SSDT-{series}.dsl'], shell=True)
        rst = os.path.join(STAGE_DIR, f'SSDT-{series}.aml')
        if os.path.exists(rst):
            shutil.move(rst, OUTPUT_DIR)
            click.echo('Finished.')
        else:
            error('Failed to hotpatch.')
    else:
        #TODO ugly, should be fixed
        execute_module('hackintosh.commands.acpi_cmd')


@cli.command(short_help='Show ACPI patches in json format.')
def info():
    click.echo('SSDT List:')
    click.secho(', '.join(LAPTOP_META['acpi']['patches']['ssdt_list']), fg='green', nl=True)

    for k in LAPTOP_META['acpi']['patches']['ssdt'].keys():
        click.echo(f"{k.upper()} Patches:")
        click.secho(', '.join(LAPTOP_META['acpi']['patches']['ssdt'][k]), fg='green', nl=True)

    click.echo('DSDT Patches:')
    click.secho(', '.join(LAPTOP_META['acpi']['patches']['dsdt']), fg='green')
