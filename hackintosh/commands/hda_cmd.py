from hackintosh import ALL_META
from hackintosh.lib import unzip, cleanup, download_kext, download
import click


@click.command(short_help='Download AppleHDA kexts or tools.')
@click.option('-a', '--alc', is_flag=True, help='Download AppleALC kext.')
@click.option('-v', '--voodoohda', is_flag=True, help='Download VoodooHDA pkg.')
@click.option('-p', '--patcher', is_flag=True, help='Download AppleHDA Patcher app & patches.')
def cli(alc, voodoohda, patcher):
    cleanup()

    if alc: download_kext(ALL_META['projects']['AppleALC'])
    if voodoohda: download_kext(ALL_META['projects']['VoodooHDA'])
    if patcher: download('https://codeload.github.com/Mirone/AppleHDAPatcher/zip/master', filename='AppleHDAPatcher-master.zip')
    unzip()
