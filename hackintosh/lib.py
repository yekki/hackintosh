from hackintosh import STAGE_DIR, OUTPUT_DIR, PKG_ROOT
from bs4 import BeautifulSoup
from urllib.request import urlopen
from inspect import signature
from distutils.dir_util import copy_tree
import requests, errno, subprocess, cgi, zipfile, os, click, shutil, glob, logging


def download_rehabman(project_name, filter=None):
    url = f'https://bitbucket.org/RehabMan/{project_name}/downloads/'
    soup = BeautifulSoup(urlopen(url), 'html.parser')
    try:
        list = [i.text for i in soup.findAll('a', {"class": "execute"})]
        if filter:
            list = [i for i in list if filter in i]

        return download(f'{url}{list[0]}', STAGE_DIR, list[0])
    except AttributeError as e:
        logging.error(f'can not found tag:{e}')


def download(url, folder=STAGE_DIR, filename=None):
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
            logging.info(output)
        else:
            logging.error(output)

    output = ret.stdout.decode()

    if output and output != 'None' and show_out: logging.info(output)

    if msg: logging.info(msg)


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
    if os.path.join(os.getcwd(), 'hackintosh') == PKG_ROOT:
        cleanup_dirs(STAGE_DIR, OUTPUT_DIR, rmdir=True)
    else:
        cleanup_dirs(STAGE_DIR, OUTPUT_DIR)

    delete_files(os.path.join(os.getcwd(), 'refs.txt'))


def unzip():
    unzip_dir(STAGE_DIR, OUTPUT_DIR)
    path = os.path.join(OUTPUT_DIR, 'Release')
    if os.path.isdir(path):
        copy_tree(path, OUTPUT_DIR)
        shutil.rmtree(path)

    for f in ('AppleALC.kext.dSYM', '__MACOSX', 'Debug', 'HWMonitor.app',
              'FakeSMC_ACPISensors.kext', 'FakeSMC_CPUSensors.kext',
              'FakeSMC_GPUSensors.kext', 'FakeSMC_LPCSensors.kext'):
        path = os.path.join(OUTPUT_DIR, f)
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)


def execute_module(module_name, context=None):
    import re, importlib
    module = importlib.import_module(f'hackintosh.commands.impl.{module_name}_impl')
    functions = sorted(filter((lambda x: re.search(r'^_\d+', x)), dir(module)))
    for f in functions:
        func = getattr(module, f)
        sig = signature(func)

        if 'ctx' in sig.parameters.keys():
            func(context)
        else:
            func()
