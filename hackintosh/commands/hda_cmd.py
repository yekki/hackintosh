from hackintosh import STAGE_DIR
from hackintosh.lib import download, unzip
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json, click, logging


def _download_alc():
    url = 'https://api.github.com/repos/vit9696/AppleALC/releases/latest'
    resp = json.loads(urlopen(url).read())
    for asset in resp['assets']:
        if 'RELEASE' in asset['name']:
            download(asset['browser_download_url'], STAGE_DIR, asset['name'])


def _download_voodoohda():
    url = 'https://sourceforge.net/projects/voodoohda/files'
    soup = BeautifulSoup(urlopen(url), 'html.parser')

    try:
        rows = soup.find('table', id='files_list').find('tbody').findAll('tr')
        for row in rows:
            filename = row.attrs['title']
            if 'pkg.zip' in filename:
                url = f'http://sourceforge.net/projects/voodoohda/files/{filename}/download'
                download(url, STAGE_DIR, filename)
                break
    except AttributeError as e:
        logging.error(f'can not found tag:{e}')


@click.command(short_help='All hda related commands')
@click.option('-a', '--alc', is_flag=True, help='Download AppleALC kext')
@click.option('-v', '--voodoohda', is_flag=True, help='Download VoodooHDA pkg')
@click.option('-p', '--patcher', is_flag=True, help='Download AppleHDA Patcher app & patches')
def cli(alc, voodoohda, patcher):
    if alc: _download_alc()
    if voodoohda: _download_voodoohda()
    if patcher: download('https://codeload.github.com/Mirone/AppleHDAPatcher/zip/master',
                         filename='AppleHDAPatcher-master.zip')

    unzip()
