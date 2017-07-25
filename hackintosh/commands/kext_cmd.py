from hackintosh import *


@click.group(help='All kext related commands')
def cli():
    cleanup()


@cli.resultcallback()
def post(ctx):
    unzip()


@cli.command(short_help='Download kexts.')
@click.option('-e', '--essential', is_flag=True, help='Download essential kexts to support laptop startup.')
@click.argument('kexts', nargs=-1, type=click.STRING)
@pass_context
def download(ctx, kexts, essential):
    if essential:
        for k in ctx.config['kext']['essential']:
            download_rehabman(k)

    for k in kexts:
        if k in ctx.config['kext']['supported']:
            download_rehabman(k)


@cli.command(short_help='Download kexts for some laptop.')
@pass_context
def laptop(ctx):
    for k in ctx.laptop['kexts']:
        download_rehabman(k)
        info(f'{k} downloaded')


@cli.command(short_help='Download kext for external device')
@click.option('-d', '--device', default='bcm94352z', required=True, type=click.Choice(['bcm94352z']),
              help='Choose the external device')
def device(device):
    if device == 'bcm94352z':
        download_rehabman('os-x-brcmpatchram')
        download_rehabman('os-x-fake-pci-id')


@cli.command(short_help='Show all supported kexts.')
@pass_context
def supported(ctx):
    print('Supported kexts:')

    for k in ctx.config['kext']['supported']:
        print(k)