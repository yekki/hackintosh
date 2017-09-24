from hackintosh.lib import download, unzip, cleanup, download_sourceforge, download_github
import click


@click.command(short_help='Download AppleHDA kexts or tools.')
@click.option('-a', '--alc', is_flag=True, help='Download AppleALC kext.')
@click.option('-v', '--voodoohda', is_flag=True, help='Download VoodooHDA pkg.')
@click.option('-p', '--patcher', is_flag=True, help='Download AppleHDA Patcher app & patches.')
def cli(alc, voodoohda, patcher):
    cleanup()

    if alc: download_github('vit9696', 'AppleALC')
    if voodoohda: download_sourceforge('voodoohda', search='pkg.zip')
    if patcher: download('https://codeload.github.com/Mirone/AppleHDAPatcher/zip/master',
                         filename='AppleHDAPatcher-master.zip')
    unzip()
