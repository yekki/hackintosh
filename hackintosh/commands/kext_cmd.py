from hackintosh import ALL_META, LAPTOP_META
from hackintosh.lib import download_rehabman, cleanup, unzip
import click


@click.group(help='Commands for download hackintosh kexts')
def cli():
    cleanup()


@cli.resultcallback()
def post(result):
    unzip()


@cli.command(short_help='Download kexts')
@click.option('-e', '--essential', is_flag=True, help='Download essential kexts to support laptop startup')
@click.argument('kexts', nargs=-1, type=click.STRING)
def download(essential, kexts):
    if essential:
        for k in ALL_META['kext']['essential']:
            download_rehabman(k)

    for k in kexts:
        if k in ALL_META['kext']['supported']:
            download_rehabman(k)


@cli.command(short_help='Download kexts for laptop')
def laptop():
    for k in LAPTOP_META['kexts']:
        download_rehabman(k)


@cli.command(short_help='Download kext for external device')
@click.option('-d', '--device', default='bcm94352z', required=True, type=click.Choice(['bcm94352z']),
              help='Choose the external device')
def device(device):
    if device == 'bcm94352z':
        download_rehabman('os-x-brcmpatchram')
        download_rehabman('os-x-fake-pci-id')


@cli.command(short_help='Show all supported kexts')
@click.option('-s', '--supported', is_flag=True, help='Show all supported kexts')
@click.option('-l', '--laptop', is_flag=True, help='Show kexts for laptop')
@click.option('-e', '--essential', is_flag=True, help='Show essential kexts for hackintosh installation')
def info(supported, laptop, essential):

    if supported:
        for k in ALL_META['kext']['supported']:
            print(k)

    if laptop:
        for k in LAPTOP_META['kexts']:
            print(k)

    if essential:
        for k in ALL_META['kext']['essential']:
            print(k)