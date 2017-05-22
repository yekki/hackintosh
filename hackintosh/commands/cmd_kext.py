from hackintosh.main import pass_context
from hackintosh.commands.impl.kext import download_alc, download_voodoohda, download_rehabman
import click


@click.group(help='All kext related commands')
def cli():
    pass

@click.command(short_help='Download essential kexts to support laptop startup.')
@pass_context
def essential(ctx):
    pass


@cli.command(short_help='Download kexts for laptop.')
@click.option('-s', '--series', default='z30-b', required=True, type=click.Choice(['t440-p', 'z30-b']), help='Choose your laptop series.')
@pass_context
def laptop(ctx, series):
    ctx.series = series


@cli.command(short_help='Download ALC kext.')
def alc():
    download_alc()

@cli.command(short_help='Download VoodooHDA kext.')
def voodoohda():
    download_voodoohda()

@cli.command(short_help='Download kext for external device')
@click.option('-d', '--device', default='bcm94352z', required=True, type=click.Choice(['bcm94352z']), help='Choose the external device')
def device(ctx, device):
    pass

