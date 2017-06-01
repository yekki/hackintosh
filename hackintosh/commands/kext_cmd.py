from hackintosh import *
from hackintosh.commands import unzip, cleanup


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
@click.option('-s', '--series', default=SUPPORTED_SERIES[0], required=True, type=click.Choice(SUPPORTED_SERIES),
              help='Choose your laptop series.')
@pass_context
def laptop(ctx, series):
    ctx.series = series
    for k in ctx.config['kext']:
        download_rehabman(k)
        info(f'{k} downloaded')


@cli.command(short_help='Download kext for external device')
@click.option('-d', '--device', default='bcm94352z', required=True, type=click.Choice(['bcm94352z']),
              help='Choose the external device')
def device(ctx, device):
    pass


@cli.command(short_help='Show all supported kexts.')
@pass_context
def supported(ctx):
    print('Supported kexts:')

    for k in ctx.config['kext']['supported']:
        print(k)
