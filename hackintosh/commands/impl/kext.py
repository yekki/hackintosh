from bs4 import BeautifulSoup
from urllib.request import urlopen
from hackintosh.utils import download, Path

import hackintosh.logger as logger
import json


def download_rehabman(project_name):
    url = f'https://bitbucket.org/RehabMan/%s/downloads/{project_name}'
    soup = BeautifulSoup(urlopen(url), 'html.parser')

    # find the latest version
    try:
        list = sorted([i.text for i in soup.findAll('a', {"class": "execute"})], reverse=True)
        url += list[0]
        download(url, Path.STAGE_DIR, list[0])
    except AttributeError as e:
        logger.error(f'can not found tag:{e}')


def download_alc():
    url = 'https://api.github.com/repos/vit9696/AppleALC/releases/latest'
    resp = json.loads(urlopen(url).read())
    for asset in resp['assets']:
        if 'RELEASE' in asset['name']:
            download(asset['browser_download_url'], Path.STAGE_DIR, asset['name'])


def download_voodoohda():
    url = 'https://sourceforge.net/projects/voodoohda/files'
    soup = BeautifulSoup(urlopen(url), 'html.parser')

    try:
        rows = soup.find('table', id='files_list').find('tbody').findAll('tr')
        for row in rows:
            filename = row.attrs['title']
            if 'pkg.zip' in filename:
                url = f'http://sourceforge.net/projects/voodoohda/files/{filename}/download'
                download(url, Path.STAGE_DIR, filename)
                break
    except AttributeError as e:
        logger.error(f'can not found tag:{e}')
