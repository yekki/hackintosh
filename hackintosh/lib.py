from hackintosh import PKG_ROOT, STAGE_DIR, OUTPUT_DIR, REPO_ROOT, LAPTOP_ROOT, LAPTOP_META
from bs4 import BeautifulSoup
from urllib.request import urlopen
from inspect import signature
from distutils.dir_util import copy_tree
from subprocess import call
from string import Template

import requests, subprocess, cgi, zipfile, os, click, shutil, glob, logging, re, importlib


def rebuild_kextcache():
    call(['sudo', '/usr/sbin/kextcache', '-i', '/'])


def download_sourceforge(project_name, nav='', search='.zip'):
    url = f'https://sourceforge.net/projects/{project_name}/files/{nav}'
    soup = BeautifulSoup(urlopen(url), 'html.parser')

    try:
        rows = soup.find('table', id='files_list').find('tbody').findAll('tr')
        for row in rows:
            filename = row.attrs['title']

            if search in filename:
                url = f'http://sourceforge.net/projects/{project_name}/files/{nav}/{filename}/download'
                download(url, STAGE_DIR, filename)
                break
    except AttributeError as e:
        logging.error(f'can not found tag:{e}')

def download_rehabman(project_name, folder=STAGE_DIR, filter=None):
    url = f'https://bitbucket.org/RehabMan/{project_name}/downloads/'
    soup = BeautifulSoup(urlopen(url), 'html.parser')
    try:
        list = [i.text for i in soup.findAll('a', {"class": "execute"})]
        if filter:
            list = [i for i in list if filter in i]

        return download(f'{url}{list[0]}', folder, list[0])
    except AttributeError as e:
        logging.error(f'can not found tag:{e}')


def cleanup():
    global STAGE_DIR, OUTPUT_DIR

    if os.path.join(os.getcwd(), 'hackintosh') == PKG_ROOT:
        cleanup_dirs(STAGE_DIR, OUTPUT_DIR, rmdir=True)
    else:
        cleanup_dirs(STAGE_DIR, OUTPUT_DIR)

    delete(os.path.join(os.getcwd(), 'refs.txt'))


def download(url, folder, filename=None):
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


def unzip_dir(from_dir, to_dir, ext='.zip'):
    for item in os.listdir(from_dir):
        if item.endswith(ext):
            unzip_file(os.path.join(from_dir, item), to_dir)


def unzip_file(file, dest_dir):
    zip_ref = zipfile.ZipFile(file)
    zip_ref.extractall(dest_dir)
    zip_ref.close()


def cleanup_dirs(*dirs, rmdir=False):
    for dir in dirs:
        if os.path.exists(dir): shutil.rmtree(dir)
        if not rmdir: os.makedirs(dir)


def copy_dir(src, dst, filter=None):
    item_list = os.listdir(src)

    if filter: item_list = [i for i in item_list if i in filter]

    for item in item_list:
        s = os.path.join(src, item)
        if os.path.exists(s): shutil.copy2(s, os.path.join(dst, item))


def unzip(todel=None):
    global STAGE_DIR, OUTPUT_DIR

    unzip_dir(STAGE_DIR, OUTPUT_DIR)
    path = os.path.join(OUTPUT_DIR, 'Release')
    if os.path.isdir(path):
        copy_tree(path, OUTPUT_DIR)
        shutil.rmtree(path)

    for f in ('AppleALC.kext.dSYM', '__MACOSX', 'Debug', '.DS_Store'):
        delete(os.path.join(OUTPUT_DIR, f))

    if todel is not None:
        for f in os.listdir(OUTPUT_DIR):
            if f not in todel:
                delete(os.path.join(OUTPUT_DIR, f))


def delete(path, ext=None, only_files=False):
    def _del(f):
        if os.path.isfile(f):
            os.remove(f)
        elif os.path.isdir(f):
            shutil.rmtree(f)

    if only_files:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if ext is None:
                    os.remove(os.path.join(dirpath, filename))
                else:
                    if filename.endswith(f'.{ext}'):
                        os.remove(os.path.join(dirpath, filename))
    else:
        if ext is None:
            _del(path)
        else:
            for f in glob.glob(f'{path}/*.{ext}'):
                _del(path)


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


def cust_acpi_patches(ext, acpi_list, dest):
    for f in [f'{item}{ext}' for item in acpi_list]:
        file = os.path.join(REPO_ROOT, 'common', 'patches', f)
        if os.path.exists(file):
            shutil.copy2(file, dest)

        # laptop spec file will overwrite common
        file = os.path.join(LAPTOP_ROOT, 'patches', f)
        if os.path.exists(file):
            shutil.copy2(file, dest)


def clover_kext_patches(patches, output, template=None):
    if template is None:
        template = Template(open(os.path.join(REPO_ROOT, 'templates', 'clover_kexts_to_patch.templ')).read())

    with open(output, 'a') as f:
        for p in patches:
            content = template.substitute(p)
            f.write(content)
