import os, json, sys, click

from hackintosh.utils import error, save_conf

__appname__ = 'Hackintosh Workbench'
__version__ = '3.6'

__all__ = ['CLIENT_SETTINGS_FILE', 'STAGE_DIR', 'OUTPUT_DIR', 'PKG_ROOT', 'REPO_ROOT', 'ENV', 'ALL_META', 'LAPTOP_ROOT',
           'LAPTOP_META', 'CLIENT_SETTINGS', 'IASL', 'PATCHMATIC']

CLIENT_SETTINGS_FILE = os.path.join(os.path.expanduser('~'), '.hackintosh.yekki.json')

STAGE_DIR = os.path.join(os.getcwd(), 'stage')
OUTPUT_DIR = os.path.join(os.getcwd(), 'output')
PKG_ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(PKG_ROOT, 'repo')

ENV = os.environ.copy()
ENV['PATH'] = f"{os.path.join(PKG_ROOT, 'bin')}:{ENV['PATH']}"

ALL_META = dict()
LAPTOP_META = dict()

# check python version
if sys.version_info < (3, 4):
    raise ValueError('Must be using Python 3.4 or above')

# load client settings
if os.path.exists(CLIENT_SETTINGS_FILE):
    CLIENT_SETTINGS = json.load(open(CLIENT_SETTINGS_FILE, 'r'))
else:
    CLIENT_SETTINGS = json.load(
        open((os.path.join(PKG_ROOT, 'repo', 'config', 'client.json'))))

    save_conf(CLIENT_SETTINGS_FILE, CLIENT_SETTINGS)
    click.echo('Default client config file is created.')

# check the repo location
if CLIENT_SETTINGS['repo_location'] == 'local': REPO_ROOT = os.path.join(os.getcwd(), 'repo')

# load default meta data
_META_PATH = os.path.join(REPO_ROOT, 'config', 'default.json')
if not os.path.exists(_META_PATH): error(f"Can not find default.json at:{REPO_ROOT}/config")
ALL_META = json.load(open(_META_PATH))

# check acpi tools
IASL = os.path.join(PKG_ROOT, 'bin', ALL_META['tools']['iasl'])
PATCHMATIC = os.path.join(PKG_ROOT, 'bin', ALL_META['tools']['patchmatic'])

if not os.path.exists(IASL): error('Can not find iasl tool.')
if not os.path.exists(PATCHMATIC): error('Can not find patchmatic tool.')

# load laptop meta data
LAPTOP_ROOT = os.path.join(REPO_ROOT, 'laptop', CLIENT_SETTINGS['current_series'])
if not os.path.exists(LAPTOP_ROOT): error(f"Unsupported laptop series: {CLIENT_SETTINGS['current_series']}")

_META_PATH = os.path.join(LAPTOP_ROOT, 'meta.json')
if os.path.exists(_META_PATH):
    LAPTOP_META = json.load(open((_META_PATH)))
else:
    error(f"Can not find meta.json at:{LAPTOP_ROOT}")
