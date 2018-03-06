from hackintosh import REPO_ROOT, CLIENT_SETTINGS, error
from bs4 import BeautifulSoup
from urllib.request import urlopen
import json, os


def _github(meta):
    if meta.get('from') == 'source':
        return {'url': f"https://codeload.github.com/{meta['account']}/{meta['project']}/zip/master",
                'name': f"{meta['project']}-master.zip"}

    url = f"https://api.github.com/repos/{meta['account']}/{meta['project']}/releases/latest"

    resp = json.loads(urlopen(url).read())

    for asset in resp['assets']:
        if meta.get('filter', 'RELEASE') in asset['name']:
            return {'url': asset['browser_download_url'], 'author': asset['uploader']['login'], 'name': asset['name'],
                    'updated_at': asset['updated_at'][:10]}

    return None


def _bitbucket(meta):
    if 'filter' in meta['options'].keys():
        f = meta['options']['filter']
    else:
        f = None

    url = f"https://bitbucket.org/{meta['account']}/{meta['project']}/downloads/"

    soup = BeautifulSoup(urlopen(url), 'html.parser')

    trs = soup.find_all('tr', class_='iterable-item')

    tr = None

    if trs:
        if f:
            for t in trs:
                if f in t.td.text:
                    tr = t
                    break
        else:
            tr = trs[0]

    if tr:
        ret = dict()
        ret['name'] = tr.find('a', class_='execute').text
        ret['author'] = tr.find('td', class_='uploaded-by').text
        ret['url'] = 'https://bitbucket.org/{}'.format(tr.find('a', class_='execute')['href'])
        ret['updated_at'] = tr.find('time').text
        return ret
    else:
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

    row = soup.find('table', id='files_list').find('tbody').find('tr')

    if row:
        return {'name': row['title'], 'url': row.th.a['href'], 'updated_at': row.find('abbr')['title'][:10],
                'size': row.find('td', attrs={'headers': 'files_size_h'}).text.replace(" ", "")}
    else:
        return None


def _local(meta):
    path = os.path.join(REPO_ROOT, 'common', 'kexts', f"{meta['project']}.kext")

    if not os.path.exists(path):
        path = os.path.join(REPO_ROOT, 'laptop', CLIENT_SETTINGS['current_series'], 'kexts', f"{meta['project']}.kext")

    if os.path.exists(path):
        return {'url': path, 'name': meta['project']}
    else:
        error(f"{meta['project']} not exist at {path}")


# for future
def _direct(meta):
    return {'url': meta['options']['url'], 'name': meta['options']['name']}


def parse(meta):
    if meta:
        return globals()[f"_{meta['source']}"](meta)
    else:
        raise ValueError('Lost project meta.')


if __name__ == '__main__':
    from hackintosh import ALL_META

    meta = parse(ALL_META['projects']['IntelGraphicsFixup'])

    print(meta)
