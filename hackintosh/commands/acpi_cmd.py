from hackintosh import LAPTOP_META, STAGE_DIR, LAPTOP_ROOT, ALL_META, PKG_ROOT, CLIENT_SETTINGS, OUTPUT_DIR, error, message
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
            message('Finished.')
        else:
            error('failed to hotpatch.')
    else:
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
