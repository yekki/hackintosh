from hackintosh import ALL_META, LAPTOP_META, OUTPUT_DIR, REPO_ROOT, CLIENT_SETTINGS
from hackintosh.lib import download_rehabman, cleanup, unzip, delete, cleanup_dirs, rebuild_kextcache, message
from string import Template
from subprocess import call
import click, os, shutil, glob


@click.group(help='Commands for download hackintosh kexts.')
def cli():
    pass


@cli.command(short_help='Download kexts.')
@click.argument('kexts', nargs=-1, type=click.STRING)
def download(kexts):
    cleanup()

    for k in kexts:
        if k in ALL_META['kext']['supported']:
            download_rehabman(k)
            unzip()
            break
    else:
        message(f'{k} is not supported.')


@cli.command(short_help='Download kexts for laptop')
def laptop():
    cleanup()

    message('Downloading essential kexts...')

    kexts = list()

    for k, v in ALL_META['kext']['essential'].items():
        download_rehabman(k)
        kexts.extend(v)
    else:
        for kk, vv in LAPTOP_META['kext'].items():
            download_rehabman(kk)
            kexts.extend(vv)
        else:
            unzip(kexts)

# TODO: add voodoo demon installation
@cli.command(short_help='Install kexts at output directory to L/E.')
def install():
    path = os.path.join(OUTPUT_DIR, 'kexts')
    if not os.path.exists(path):
        path = OUTPUT_DIR

    for k in os.listdir(path):
        if k.endswith('.kext'):
            call(['sudo', 'cp', '-rf', os.path.join(path, k), '/Library/Extensions/'])
    else:
        rebuild_kextcache()


@cli.command(short_help='Show all supported kexts.')
@click.option('-s', '--supported', is_flag=True, help='Show all supported kext projects.')
@click.option('-l', '--laptop', is_flag=True, help='Show kexts for current laptop.')
@click.option('-e', '--essential', is_flag=True, help='Show essential kexts for hackintosh installation.')
def info(supported, laptop, essential):
    if supported:
        message('Supported kext projects:')
        for k in ALL_META['kext']['supported']:
            message(k, fg='green')

    if laptop:
        message(f"kexts for laptop {CLIENT_SETTINGS['current_series']}:")
        for k, v in LAPTOP_META['kext'].items():
            kexts = ','.join(v)
            message(f"{k}: {kexts}", fg='green')

    if essential:
        message('kexts for all laptops:')
        for k, v in ALL_META['kext']['essential'].items():
            kexts = ','.join(v)
            message(f"{k}: {kexts}", fg='green')
