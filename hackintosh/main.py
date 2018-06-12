from hackintosh import IASL, CLIENT_SETTINGS, LAPTOP_ROOT, ALL_META, STAGE_DIR, OUTPUT_DIR, LAPTOP_META, PKG_ROOT, \
    CLIENT_SETTINGS_FILE

from hackintosh.utils import delete, to_num, error
from hackintosh.commands import *

from subprocess import call

import click, os, shutil


@click.group()
def cli():
    pass


@cli.command(short_help='Cleanup stage & output directories.')
@click.confirmation_option(help='Cleanup stage & output directories.',
                           prompt="Are you sure you want to stage & output directories?")
@cleanup
def clean():
    click.clear()


@cli.command(short_help='Update tools & patches.')
@click.option('-a', '--all', is_flag=True, help='Update all tools & patches.')
@click.option('-t', '--tool', type=click.Choice(['iasl', 'patchmatic', 'patches', 'ssdtPRgen']),
              help='Chosen the tool which will be updated.')
@click.pass_context
@cleanup
def update(ctx, all, tool):
    if all:
        execute_module('update')
    elif tool:
        execute_func('update', tool)
    else:
        click.echo(ctx.get_help())


@cli.command(short_help="Edit client config file.")
def edit():
    click.edit(filename=CLIENT_SETTINGS_FILE)


@cli.command(short_help=f"Download kexts for laptop:{CLIENT_SETTINGS['current_series']}")
@cleanup
def laptop():
    click.echo(f"Downloading kexts for laptop: {CLIENT_SETTINGS['current_series']}:")

    kexts = []

    k1 = download_kexts(ALL_META['patches']['system']['kexts'])
    k2 = download_kexts(LAPTOP_META['kexts'])

    kexts.extend(k1)
    kexts.extend(k2)

    unzip(kexts)


@cli.command(short_help="Commands for external devices.")
@click.option('-i', '--id', required=True, type=click.Choice(ALL_META['external_device'].keys()),
              help='Choose the device id')
@cleanup
def device(id):
    kexts = download_kexts(ALL_META['external_device'][id]['kexts'])

    delete(os.path.join(OUTPUT_DIR, 'kexts'))
    delete(os.path.join(OUTPUT_DIR, 'clover'))

    unzip(kexts, 'kexts')

    clover_kext_patches(ALL_META['external_device'][id]['clover']['kexts_to_patch'],
                        os.path.join(OUTPUT_DIR, 'clover', 'patch.plist'))


@cli.command(short_help='Prepare all stuff for device.')
@click.option('-p', '--patch', required=True, type=click.Choice(ALL_META['patches'].keys()),
              help='Choose the laptop series')
@cleanup
def patch(patch):
    execute_func('patch', patch)


@cli.command(short_help='Show all kext projects.')
@click.option('-s', '--scope', required=True, type=click.Choice(['supported', 'laptop', 'common']),
              help='Choose the scope of kexts')
@click.option('-d', '--dynamic', is_flag=True, help='Show last update date.')
def kext_info(scope, dynamic):
    if scope == 'supported':
        click.secho('Supported kexts projects:', bold=True)
        [print_project(v, dynamic) for v in ALL_META['projects'].values() if v['type'] == 'kext']
    elif scope == 'laptop':
        click.secho(f"kexts for laptop {CLIENT_SETTINGS['current_series']}:", bold=True)
        projects = {}
        projects.update(LAPTOP_META['kexts'])
        projects.update(ALL_META['patches']['system']['kexts'])
        for k, v in projects.items():
            pmeta = ALL_META['projects'][k]
            kexts = ', '.join(v)
            print_project(pmeta, kexts, dynamic)
    elif scope == 'common':
        click.echo('kexts for all laptops:')
        for k, v in ALL_META['patches']['system']['kexts'].items():
            pmeta = ALL_META['projects'][k]
            kexts = ','.join(v)
            print_project(pmeta, kexts, dynamic)


@cli.command(short_help='Download projects.')
@click.argument('projects', nargs=-1, type=click.STRING)
@click.pass_context
@cleanup
def download(ctx, projects):
    if not projects:
        print(ctx.get_help())
    for p in projects:
        if p in ALL_META['projects'].keys():
            download_project(ALL_META['projects'][p])
        else:
            click.echo(f'{p} is not supported.')
    unzip()


@cli.command(short_help='Show all app projects.')
def app_info():
    click.secho('Supported app projects:', bold=True)
    [print_project(v) for v in ALL_META['projects'].values() if v['type'] == 'app']

    click.secho('Supported pkg projects:', bold=True)
    [print_project(v) for v in ALL_META['projects'].values() if v['type'] == 'pkg']


@cli.command(short_help='Clone local Repository.')
def clone():
    shutil.copytree(os.path.join(PKG_ROOT, 'repo'),
                    os.path.join(os.getcwd(), 'repo'))
    click.echo('Created local repository stub directory.')


@cli.command(short_help='Open output in finder.')
def output():
    click.launch(OUTPUT_DIR)


@cli.command(short_help='Show current client settings.')
def client_info():
    click.secho('Hackintosh Workbench Version: ', bold=True)
    click.secho(CLIENT_SETTINGS['version'], fg='green')
    click.secho('Laptop Series: ', bold=True)
    click.secho(CLIENT_SETTINGS['current_series'], fg='green')
    click.secho('Repository Location: ', bold=True)
    click.secho(CLIENT_SETTINGS['repo_location'], fg='green')


@cli.command(short_help='Set default laptop series.')
@click.option('-s', '--series', required=True, type=click.Choice(ALL_META['certified']['series']),
              help='Choose the laptop series')
def series(series):
    if series in ALL_META['certified']['series']:
        CLIENT_SETTINGS['current_series'] = series
        update_client_conf()
        click.echo(f'Your current laptop series is {series}')
    else:
        click.echo(f'{series} does not exist.')


@cli.command(short_help='Open urls.')
def open():
    ans = True
    while ans:

        click.echo('\n'.join([f"{i+1}.{v['desc']}" for i, v in enumerate(ALL_META['bookmark'])]) + "\n" + str(
            len(ALL_META['bookmark']) + 1) + '.Exit\n')

        click.echo("What would you like to access? ")
        ans = click.getchar()

        index = to_num(ans)

        if index == 0:
            click.secho("\n Not Valid Choice Try again", fg="red")
        elif index == len(ALL_META['bookmark']) + 1:
            click.echo("\n Goodbye")
            ans = None
        else:
            m = ALL_META['bookmark'][index - 1]

            if m['uri'].startswith('http'):
                click.launch(m['uri'])
            else:
                click.launch(m['uri'], locate=True)
        click.clear()


@cli.command(short_help='Build & patch ACPI files.')
@click.option('-h', '--hotpatch', is_flag=True, help='Build hotpatches')
@cleanup
def acpi_build(hotpatch):
    if hotpatch:
        src = os.path.join(LAPTOP_ROOT, 'patches', 'hot')
        series = CLIENT_SETTINGS['current_series'].upper()
        for f in os.listdir(src):
            shutil.copy2(os.path.join(src, f), os.path.join(STAGE_DIR, f))

        os.chdir(STAGE_DIR)
        call([f'{IASL} SSDT-{series}.dsl'], shell=True)
        rst = os.path.join(STAGE_DIR, f'SSDT-{series}.aml')
        if os.path.exists(rst):
            shutil.move(rst, OUTPUT_DIR)
            click.echo('Finished.')
        else:
            error('Failed to hotpatch.')
    else:
        # TODO ugly, should be fixed
        execute_module('acpi')


@cli.command(short_help='Show ACPI patches in json format.')
def acpi_info():
    click.secho(f"{LAPTOP_META['description']}\n", bold=True)
    click.secho('SSDT List:', bold=True)
    click.secho(', '.join(LAPTOP_META['acpi']['patches']['ssdt_list']), fg='green', nl=True)

    for k in LAPTOP_META['acpi']['patches']['ssdt'].keys():
        click.secho(f"{k.upper()} Patches:", bold=True)
        click.secho(', '.join(LAPTOP_META['acpi']['patches']['ssdt'][k]), fg='green', nl=True)

    click.secho('DSDT Patches:', bold=True)
    click.secho(', '.join(LAPTOP_META['acpi']['patches']['dsdt']), fg='green')


@cli.command(short_help="Debug command.")
def debug():
    """Demonstrates using the pager."""
    pass


if __name__ == '__main__':
    cli()
