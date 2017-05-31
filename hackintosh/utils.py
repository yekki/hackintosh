from distutils.dir_util import copy_tree
from bs4 import BeautifulSoup
from urllib.request import urlopen
from inspect import signature
import hackintosh.logger as logger
import importlib, requests, errno, re, sys, click, json, subprocess, os, cgi, zipfile, shutil, glob


class Path:
    STAGE_DIR = os.path.join(os.getcwd(), 'stage')
    OUTPUT_DIR = os.path.join(os.getcwd(), 'output')
    PKG_ROOT = os.path.dirname(os.path.abspath(__file__))
    PKG_REPO = os.path.join(PKG_ROOT, 'repo')
    CWD_REPO = os.path.join(os.getcwd(), 'repo')
    RECORDER_FILE = os.path.join(os.getcwd(), 'recorder.log')


class Context:
    def __init__(self):
        self._config = {}
        self._laptop = {}
        self._series = None
        self._is_local_repo = False

    @property
    def is_local_repo(self):
        return self._is_local_repo

    @is_local_repo.setter
    def is_local_repo(self, local):
        self._is_local_repo = local
        self._config = load_json(os.path.join(self.repo_path, 'config', 'default.json'))

    @property
    def config(self):

        if not self._config:
            self._config = load_json(os.path.join(Path.PKG_REPO, 'config', 'default.json'))

        return self._config

    @property
    def series(self):
        return self._series

    @series.setter
    def series(self, s):
        self._series = s

    @property
    def repo_path(self):
        if self.is_local_repo:
            return Path.CWD_REPO
        else:
            return Path.PKG_REPO

    @property
    def laptop_path(self):
        return os.path.join(self.repo_path, 'laptop', self.series)

    @property
    def laptop(self):
        if (not self._laptop) or (self._laptop and self._laptop['series'] != self._series):
            self._laptop = load_json(os.path.join(self.repo_path, 'laptop', self._series, 'meta.json'))

        return self._laptop


def check_py_ver():
    alert = 'Must be using Python 3.4 or above'
    if sys.version_info.major >= 3:
        if sys.version_info.minor < 4:
            raise alert
    else:
        raise alert


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


def dir_del(src, ext='*'):
    files = glob.glob(f'{src}/*.{ext}')
    for f in files:
        os.remove(f)


def dir_copy(src, dst, filter=None):
    item_list = os.listdir(src)

    if filter != None:
        item_list = [i for i in item_list if i in filter]

    for item in item_list:
        s = os.path.join(src, item)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(dst, item))


def load_json(filename):
    with open(filename) as f:
        data = json.load(f)

    return data


def execute_module(module_name, context=None):
    module = importlib.import_module(f'hackintosh.{module_name}')
    functions = sorted(filter((lambda x: re.search(r'^_\d+', x)), dir(module)))
    for f in functions:
        func = getattr(module, f)
        sig = signature(func)

        if 'ctx' in sig.parameters.keys():
            func(context)
        else:
            func()


def execute(name, ctx=None):
    module = importlib.import_module(f'hackintosh.{name}')
    cmd_list = getattr(module, 'COMMANDS')

    for cmd in cmd_list:
        if ctx:
            getattr(module, cmd)(ctx)
        else:
            getattr(module, cmd)()


def run(cmds, msg=None, show_out=True, ignore_error=False):
    if logger.RECORDER:
        for c in cmds:
            logger.record(c)
    else:
        if os.path.isfile(Path.RECORDER_FILE):
            os.remove(Path.RECORDER_FILE)

    ret = subprocess.run(cmds, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    output = ret.stderr.decode()
    if output and output != 'None' and show_out:
        if ignore_error:
            logger.info(output)
        else:
            logger.error(output)

    output = ret.stdout.decode()

    if output and output != 'None' and show_out: logger.info(output)

    if msg: logger.info(msg)


def cleanup():
    if os.path.join(os.getcwd(), 'hackintosh') == Path.PKG_ROOT:
        cleanup_dirs(Path.STAGE_DIR, Path.OUTPUT_DIR, rmdir=True)
    else:
        cleanup_dirs(Path.STAGE_DIR, Path.OUTPUT_DIR)

    delete_file(os.path.join(os.getcwd(), 'refs.txt'))


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


def cprint(msg, color='green'):
    click.echo(click.style(msg, fg=color))


# only delete files
def delete_files(dir):
    for dirpath, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            os.unlink(os.path.join(dirpath, filename))


def delete_file(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise


def download_rehabman(project_name, filter=None):
    url = f'https://bitbucket.org/RehabMan/{project_name}/downloads/'
    soup = BeautifulSoup(urlopen(url), 'html.parser')
    try:
        list = [i.text for i in soup.findAll('a', {"class": "execute"})]
        if filter:
            list = [i for i in list if filter in i]

        return download(f'{url}{list[0]}', Path.STAGE_DIR, list[0])
    except AttributeError as e:
        logger.error(f'can not found tag:{e}')
