from hackintosh import ALL_META, LAPTOP_META, OUTPUT_DIR, REPO_ROOT, CLIENT_SETTINGS
from hackintosh.lib import download_kext, cleanup, unzip, delete, cleanup_dirs, rebuild_kextcache, message
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
            download(k)
        else:
            message(f'{k} is not supported.')

    unzip()


@cli.command(short_help='Download kexts for laptop')
def laptop():
    cleanup()

    message(f"Downloading kexts for laptop {CLIENT_SETTINGS['current_series']}:")

    kexts = []
    projects = {}

    projects.update(ALL_META['kext']['essential'])
    projects.update(LAPTOP_META['kext'])

    for k, v in projects.items():
        kext = ALL_META['kext']['supported'][k]
        download_kext(kext)
        kexts.extend(v)
    else:
        unzip(kexts)


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
        for k, v in ALL_META['kext']['essential'].items():
            kexts = ','.join(v)
            message(f"{k}: {kexts}", fg='green')

    if essential:
        message('kexts for all laptops:')
        for k, v in ALL_META['kext']['essential'].items():
            kexts = ','.join(v)
            message(f"{k}: {kexts}", fg='green')
