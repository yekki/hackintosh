import os, json, sys, logging

if sys.version_info < (3, 4):
    raise 'Must be using Python 3.4 or above'

logging.basicConfig(level=logging.INFO, format='%(asctime)s : %(levelname)s : %(message)s')

CLIENT_SETTINGS_FILE = os.path.join(os.path.expanduser('~'), '.yekki.json')
STAGE_DIR = os.path.join(os.getcwd(), 'stage')
OUTPUT_DIR = os.path.join(os.getcwd(), 'output')
PKG_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(PKG_ROOT, 'repo')


def save_conf(data=None):
    if data is None:
        data = json.load(
            open((os.path.join(PKG_ROOT, 'repo', 'config', 'client.json'))))

    with open(CLIENT_SETTINGS_FILE, 'w', encoding='utf8') as f:
        f.write(json.dumps(data,
                           indent=4, sort_keys=True,
                           separators=(',', ': '), ensure_ascii=False))
    return data


if os.path.isfile(CLIENT_SETTINGS_FILE):
    CLIENT_SETTINGS = save_conf(data=json.load(open(CLIENT_SETTINGS_FILE, 'r')))
else:
    CLIENT_SETTINGS = save_conf()

if CLIENT_SETTINGS['repo_location'] == 'local':
    REPO_ROOT = os.path.join(os.getcwd(), 'repo')

LAPTOP_ROOT = os.path.join(REPO_ROOT, 'laptop', CLIENT_SETTINGS['current_series'])

_META_PATH = os.path.join(REPO_ROOT, 'config', 'default.json')

if os.path.exists(_META_PATH):
    ALL_META = json.load(open(_META_PATH))

    _META_PATH = os.path.join(LAPTOP_ROOT, 'meta.json')

    if os.path.exists(_META_PATH):
        LAPTOP_META = json.load(open((_META_PATH)))
    else:
        raise LookupError(
            f"can not found meta.json at local repository directory for laptop series:{CLIENT_SETTINGS['current_series']}")
else:
    raise LookupError('can not found default.json at local repository directory')
