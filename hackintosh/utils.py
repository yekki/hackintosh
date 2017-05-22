import hackintosh.logger as logger
import importlib, requests, sys, click, json, subprocess, os, cgi, zipfile, shutil, glob, inspect


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


def download(url, folder, filename=None):
    assert os.path.isdir(folder)
    """Function for downloading stuff"""
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


def unzip_dir(from_dir, to_dir, extension='.zip'):
    assert os.path.isdir(from_dir)
    assert os.path.isdir(to_dir)

    for item in os.listdir(from_dir):
        if item.endswith(extension):
            file_name = os.path.join(from_dir, item)
            zip_ref = zipfile.ZipFile(file_name)
            zip_ref.extractall(to_dir)
            zip_ref.close()


def cleanup_dirs(*dirs):
    for dir in dirs:
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.makedirs(dir)


def dir_del(src, ext='*'):
    assert os.path.isdir(src)

    files = glob.glob('%s/*.%s' % (src, ext))
    for f in files:
        os.remove(f)


def dir_copy(src, dst, filter=None):
    assert os.path.exists(src)
    assert os.path.exists(dst)

    item_list = os.listdir(src)

    if filter != None:
        item_list = [i for i in item_list if i in filter]

    for item in item_list:
        s = os.path.join(src, item)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(dst, item))


def load_json(filename):
    assert os.path.isfile(filename)
    with open(filename) as f:
        data = json.load(f)

    return data


def execute(ctx, name):
    assert ctx != None
    assert name != None

    module = importlib.import_module(f'hackintosh.commands.impl.{name}')
    cmd_list = getattr(module, 'COMMANDS')

    for cmd in cmd_list:
        getattr(module, cmd)(ctx)


def run(cmds, msg=None, show_stdout=True):
    assert cmds != None

    if logger.RECORDER:
        for c in cmds:
            logger.record(c)
    else:
        if os.path.isfile(Path.RECORDER_FILE):
            os.remove(Path.RECORDER_FILE)

    ret = subprocess.run(cmds, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    output = ret.stderr.decode()
    if output: logger.error(output)
    output = ret.stdout.decode()
    if output and show_stdout: logger.info(output)

    if msg: logger.info(msg)


def cleanup():
    cleanup_dirs(Path.STAGE_DIR, Path.OUTPUT_DIR)


def whoami():
    frame = inspect.currentframe()
    return inspect.getframeinfo(frame = inspect.currentframe()).function
