import os, json, sys, logging, click

if sys.version_info < (3, 4):
    raise 'Must be using Python 3.4 or above'


def error(msg):
    click.echo(click.style(msg, fg='red'))
    exit(-1)


def message(msg):
    if isinstance(msg, dict):
        str = ''
        for k, v in msg.items():
            str += click.style(k, fg=v)
        click.echo(str)
    else:
        click.echo(click.style(msg, fg='blue'))


logging.basicConfig(level=logging.INFO, format='%(asctime)s : %(levelname)s : %(message)s')

CLIENT_SETTINGS_FILE = os.path.join(os.path.expanduser('~'), '.yekki.json')
STAGE_DIR = os.path.join(os.getcwd(), 'stage')
OUTPUT_DIR = os.path.join(os.getcwd(), 'output')
PKG_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(PKG_ROOT, 'repo')

ALL_META = dict()
LAPTOP_META = dict()


def save_conf(data=None):
    if data is None:
        data = json.load(
            open((os.path.join(PKG_ROOT, 'repo', 'config', 'client.json'))))

    with open(CLIENT_SETTINGS_FILE, 'w', encoding='utf8') as f:
        f.write(json.dumps(data,
                           indent=4, sort_keys=True,
                           separators=(',', ': '), ensure_ascii=False))
    return data


# check client config file, if not found then create new one
if os.path.isfile(CLIENT_SETTINGS_FILE):
    CLIENT_SETTINGS = save_conf(data=json.load(open(CLIENT_SETTINGS_FILE, 'r')))
else:
    CLIENT_SETTINGS = save_conf()

if CLIENT_SETTINGS['repo_location'] == 'local':
    REPO_ROOT = os.path.join(os.getcwd(), 'repo')

LAPTOP_ROOT = os.path.join(REPO_ROOT, 'laptop', CLIENT_SETTINGS['current_series'])

_META_PATH = os.path.join(REPO_ROOT, 'config', 'default.json')

# check meta file in repository
if not os.path.exists(_META_PATH):
    CLIENT_SETTINGS['repo_location'] = 'pkg'
    save_conf(CLIENT_SETTINGS)
    REPO_ROOT = os.path.join(PKG_ROOT, 'repo')
    logging.info("Can't find local repository, auto switch to pkg repository.")
    _META_PATH = os.path.join(REPO_ROOT, 'config', 'default.json')
    LAPTOP_ROOT = os.path.join(REPO_ROOT, 'laptop', CLIENT_SETTINGS['current_series'])

# load global meta data
if os.path.exists(_META_PATH):
    ALL_META = json.load(open(_META_PATH))
else:
    raise LookupError(
        f"Can't find not found system meta file:{_META_PATH}")

# load laptop meta data
_META_PATH = os.path.join(LAPTOP_ROOT, 'meta.json')

if os.path.exists(_META_PATH):
    LAPTOP_META = json.load(open((_META_PATH)))
else:
    raise LookupError(
        f"can't find laptop meta file: {_META_PATH}")

if not bool(ALL_META): raise ValueError("The global meta data is empty.")
if not bool(LAPTOP_META): raise ValueError("The laptop meta data is empty.")
