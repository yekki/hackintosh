from bs4 import BeautifulSoup
from urllib.request import urlopen
from inspect import signature
from distutils.dir_util import copy_tree
from enum import Enum, unique

import requests, errno, subprocess, cgi, zipfile, stat, pprint
import os, click, json, sys, shutil, glob, logging, re, importlib


@unique
class Path(Enum):
    STAGE_DIR = os.path.join(os.getcwd(), 'stage')
    OUTPUT_DIR = os.path.join(os.getcwd(), 'output')
    PKG_ROOT = os.path.dirname(os.path.abspath(__file__))
    PKG_REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'repo')
    CWD_REPO = os.path.join(os.getcwd(), 'repo')
    CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.yekki.json')


logging.basicConfig(level=logging.INFO, format='%(asctime)s : %(levelname)s : %(message)s')


class MainCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []

        for fn in os.listdir(os.path.join(Path.PKG_ROOT, 'commands')):
            rv.append(fn)

        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__(f'hackintosh.commands.{name}_cmd', None, None, ['cli'])

        except ImportError as e:
            critical(e)
        else:
            return mod.cli


class Context:
    def __init__(self):
        self._config = {}
        self._laptop = {}
        self._config = json.load(open(os.path.join(self.repo_path, 'config', 'default.json')))

    @property
    def config(self):

        if not self._config:
            self._config = json.load(open(os.path.join(Path.PKG_REPO, 'config', 'default.json')))

        return self._config

    @property
    def repo_path(self):
        if CONFIG['repo_location'] == 'local':
            return Path.CWD_REPO
        elif CONFIG['repo_location'] == 'pkg':
            return Path.PKG_REPO
        else:
            raise ValueError

    @property
    def laptop_path(self):
        return os.path.join(self.repo_path, 'laptop', CONFIG['current_series'])

    @property
    def laptop(self):
        if (not self._laptop) or (self._laptop and self._laptop['series'] != CONFIG['current_series']):
            self._laptop = json.load(
                open((os.path.join(self.repo_path, 'laptop', CONFIG['current_series'], 'meta.json'))))

        return self._laptop


def download_rehabman(project_name, filter=None):
    url = f'https://bitbucket.org/RehabMan/{project_name}/downloads/'
    soup = BeautifulSoup(urlopen(url), 'html.parser')
    try:
        list = [i.text for i in soup.findAll('a', {"class": "execute"})]
        if filter:
            list = [i for i in list if filter in i]

        return download(f'{url}{list[0]}', Path.STAGE_DIR, list[0])
    except AttributeError as e:
        error(f'can not found tag:{e}')


def download(url, folder=Path.STAGE_DIR, filename=None):
    r = requests.get(url, stream=True)

    if not filename:
        if "Content-Disposition" in r.headers:
            _, params = cgi.parse_header(r.headers["Content-Disposition"])
            filename = params["filename"]
        else:
            filename = url.split("/")[-1]

    total_length = int(r.headers.get('content-length'))
    download_file_path = os.path.join(folder, filename)
    with open(download_file_path, "wb") as f:
        expected_size = (total_length / 1024) + 1
        with click.progressbar(r.iter_content(1024), length=expected_size, bar_template='%(label)s  %(bar)s | %(info)s',
                               label=filename, fill_char=click.style(u'█', fg='cyan'),
                               empty_char=' ') as chunks:
            for chunk in chunks:
                f.write(chunk)
                f.flush()

    return filename


def unzip_dir(from_dir, to_dir, extension='.zip'):
    for item in os.listdir(from_dir):
        if item.endswith(extension):
            file = os.path.join(from_dir, item)
            unzip_file(file, to_dir)


def unzip_file(file, dest_dir):
    zip_ref = zipfile.ZipFile(file)
    zip_ref.extractall(dest_dir)
    zip_ref.close()


def cleanup_dirs(*dirs, rmdir=False):
    for dir in dirs:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        if not rmdir: os.makedirs(dir)


def del_dir(src, ext='*'):
    files = glob.glob(f'{src}/*.{ext}')
    for f in files:
        os.remove(f)


def copy_dir(src, dst, filter=None):
    item_list = os.listdir(src)

    if filter:
        item_list = [i for i in item_list if i in filter]

    for item in item_list:
        s = os.path.join(src, item)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(dst, item))


def run(cmds, msg=None, show_out=True, ignore_error=False):
    ret = subprocess.run(cmds, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    output = ret.stderr.decode()

    if output and output != 'None' and show_out:
        if ignore_error:
            info(output)
        else:
            error(output)

    output = ret.stdout.decode()

    if output and output != 'None' and show_out: info(output)

    if msg: info(msg)


def cprint(msg, color='green'):
    click.echo(click.style(msg, fg=color))


def info(msg):
    logging.info(click.style(msg, fg='blue'))


def warning(msg):
    logging.warning(click.style(msg, fg='yellow'))


def error(msg):
    logging.error(click.style(msg, fg='magenta'))


def critical(msg):
    logging.critical(click.style(msg, fg='red'))
    exit(-1)


# only delete files
def delete_files(path):
    if os.path.isdir(path):
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                os.unlink(os.path.join(dirpath, filename))
    elif os.path.isfile(path):
        try:
            os.remove(path)
        except OSError as e:
            if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
                raise


def cleanup():
    if os.path.join(os.getcwd(), 'hackintosh') == Path.PKG_ROOT:
        cleanup_dirs(Path.STAGE_DIR, Path.OUTPUT_DIR, rmdir=True)
    else:
        cleanup_dirs(Path.STAGE_DIR, Path.OUTPUT_DIR)

    delete_files(os.path.join(os.getcwd(), 'refs.txt'))


def unzip():
    unzip_dir(Path.STAGE_DIR, Path.OUTPUT_DIR)
    path = os.path.join(Path.OUTPUT_DIR, 'Release')
    if os.path.isdir(path):
        copy_tree(path, Path.OUTPUT_DIR)
        shutil.rmtree(path)

    for f in ('AppleALC.kext.dSYM', '__MACOSX', 'Debug', 'HWMonitor.app',
              'FakeSMC_ACPISensors.kext', 'FakeSMC_CPUSensors.kext',
              'FakeSMC_GPUSensors.kext', 'FakeSMC_LPCSensors.kext'):
        path = os.path.join(Path.OUTPUT_DIR, f)
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)


def execute_module(module_name, context=None):
    module = importlib.import_module(f'hackintosh.commands.impl.{module_name}_impl')
    functions = sorted(filter((lambda x: re.search(r'^_\d+', x)), dir(module)))
    for f in functions:
        func = getattr(module, f)
        sig = signature(func)

        if 'ctx' in sig.parameters.keys():
            func(context)
        else:
            func()


def save_conf(data=None):
    if not data:
        data = _DEFAUT_CONF

    with open(Path.CONFIG_FILE, 'w', encoding='utf8') as f:
        f.write(json.dumps(data,
                           indent=4, sort_keys=True,
                           separators=(',', ': '), ensure_ascii=False))
    return data

#### main ####

_DEFAUT_CONF = {'version': '1.1', 'repo_location': 'pkg', 'current_series': 'z30-b',
                'supported_series': ('z30-b', 't440p'),
                'context_settings': dict(auto_envvar_prefix='yekki')}

pass_context = click.make_pass_decorator(Context, ensure=True)

if sys.version_info < (3, 4):
    raise 'Must be using Python 3.4 or above'

if os.path.isfile(Path.CONFIG_FILE):
    CONFIG = save_conf(data=json.load(open(Path.CONFIG_FILE, 'r')))
else:
    CONFIG = save_conf()

if CONFIG.get('version', -1) != _DEFAUT_CONF['version']:
    CONFIG = save_conf()
