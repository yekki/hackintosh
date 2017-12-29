from hackintosh import REPO_ROOT, error, debug
from bs4 import BeautifulSoup
from urllib.request import urlopen
import json, os


def _get(meta, key, default):
    if key in meta['options'].keys():
        return meta['options'][key]
    else:
        return default

def _github(meta):
    f = _get(meta, 'from', None)

    if f == 'source':
        return {'url': f"https://codeload.github.com/{meta['account']}/{meta['project']}/zip/master", 'name':f"{meta['project']}-master.zip"}

    url = f"https://api.github.com/repos/{meta['account']}/{meta['project']}/releases/latest"
    resp = json.loads(urlopen(url).read())

    for asset in resp['assets']:
        if _get(meta, 'filter', 'RELEASE') in asset['name']:
            return {'url': asset['browser_download_url'], 'name': asset['name']}

    return None


def _bitbucket(meta):
    if 'filter' in meta['options'].keys():
        f = meta['options']['filter']
    else:
        f = None

    url = f"https://bitbucket.org/{meta['account']}/{meta['project']}/downloads/"
    soup = BeautifulSoup(urlopen(url), 'html.parser')
    try:
        list = [i.text for i in soup.findAll('a', {"class": "execute"})]

        if f:
            list = [i for i in list if f in i]

        if list:
            return {'url': f'{url}{list[0]}', 'name': list[0]}
        else:
            return None
    except AttributeError as e:
        debug(e)
        error(f"Can's found tag.")

    return None


def _sourceforge(meta):
    if 'nav' in meta['options'].keys():
        n = meta['options']['nav']
    else:
        n = ''

    if 'ext' in meta['options'].keys():
        e = meta['options']['ext']
    else:
        e = 'zip'

    url = f"https://sourceforge.net/projects/{meta['project']}/files/{n}"

    soup = BeautifulSoup(urlopen(url), 'html.parser')
    try:
        rows = soup.find('table', id='files_list').find('tbody').findAll('tr')
        for row in rows:
            filename = row.attrs['title']
            if str(filename).endswith(e):
                url = f"http://sourceforge.net/projects/{meta['project']}/files/{n}/{filename}/download"
                return {'url': url, 'name': filename}
    except AttributeError as e:
        debug(e)
        error(f"Can's found tag.")

    return None


def _local(meta):
    return {'url': os.path.join(REPO_ROOT, 'common', 'kexts', f"{meta['project']}.kext"), 'name': meta['project']}

# for future
def _direct(meta):
    return {'url': meta['options']['url'], 'name': meta['options']['name']}

def parse(meta):
    if meta:
        return globals()[f"_{meta['source']}"](meta)
    else:
        raise ValueError('Lost project meta.')