from hackintosh.utils import unzip, download
from hackintosh.hda import download_alc, download_voodoohda
import click


@click.command(short_help='All hda related commands')
@click.option('-a', '--alc', is_flag=True, help='Download AppleALC kext')
@click.option('-v', '--voodoohda', is_flag=True, help='Download VoodooHDA pkg')
@click.option('-p', '--patcher', is_flag=True, help='Download AppleHDA Patcher app & patches')
def cli(alc, voodoohda, patcher):
    if alc: download_alc()
    if voodoohda: download_voodoohda()
    if patcher: download('https://codeload.github.com/Mirone/AppleHDAPatcher/zip/master', filename='AppleHDAPatcher-master.zip')

    unzip()


