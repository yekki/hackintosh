import click

from hackintosh.main import pass_context
from hackintosh.utils import unzip, download_rehabman

@click.group(help='All kext related commands')
def cli():
    pass


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
@click.option('-s', '--series', default='z30-b', required=True, type=click.Choice(['t440-p', 'z30-b']), help='Choose your laptop series.')
@pass_context
def laptop(ctx, series):
    ctx.series = series


@cli.command(short_help='Download kext for external device')
@click.option('-d', '--device', default='bcm94352z', required=True, type=click.Choice(['bcm94352z']), help='Choose the external device')
def device(ctx, device):
    pass

@cli.command(short_help='Show all supported kexts.')
@pass_context
def supported(ctx):
    print('Supported kexts:')

    for k in ctx.config['kext']['supported']:
        print(k)


