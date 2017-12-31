from hackintosh import PKG_ROOT, REPO_ROOT, ALL_META, STAGE_DIR, OUTPUT_DIR, DEBUG
from hackintosh.parser import parse
from inspect import signature
from distutils.dir_util import copy_tree
from subprocess import call
from string import Template

import requests, cgi, zipfile, os, click, shutil, re, importlib


def execute(cmd, filename=None):
    if filename is None:
        call(cmd, shell=True)
    else:
        with open(os.path.join(STAGE_DIR, filename), 'wb') as f:
            call(cmd, stdout=f, stderr=f, shell=True)


def zip_dir(path, filename, suffix=None):
    zipf = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        for file in files:
            if suffix is None:
                zipf.write(os.path.join(root, file))
            else:
                if file.endswith(suffix):
                    zipf.write(os.path.join(root, file))


def print_project(meta, kexts=None):
    click.echo(f"- Project Name: {meta['project']} Author: {meta['account']}")
    if kexts:
        click.secho(f'  {kexts}', fg='green')



def cleanup_dir(path):
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


def delete(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


def rebuild_kextcache():
    call(['sudo', '/usr/sbin/kextcache', '-i', '/'])


def download_project(meta):
    p = parse(meta)
    if p:
        return download(p['url'], p['name'])
    else:
        raise ValueError(f'Failed to parse project meta:{meta}')


def download(url, filename=None, folder=STAGE_DIR):
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
                               label=filename, fill_char=click.style(
                                   u'█', fg='cyan'),
                               empty_char=' ') as chunks:
            for chunk in chunks:
                f.write(chunk)
                f.flush()

    return filename


def cleanup():
    if os.path.join(os.getcwd(), 'hackintosh') == PKG_ROOT:
        cleanup_dirs(STAGE_DIR, OUTPUT_DIR, rmdir=True)
    else:
        cleanup_dirs(STAGE_DIR, OUTPUT_DIR)

    delete(os.path.join(os.getcwd(), 'refs.txt'))


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
        if os.path.exists(dir):
            shutil.rmtree(dir)
        if not rmdir:
            os.makedirs(dir)


def copy_dir(src, dst, filter=None):
    item_list = os.listdir(src)

    if filter:
        item_list = [i for i in item_list if i in filter]

    for item in item_list:
        s = os.path.join(src, item)
        if os.path.exists(s):
            shutil.copy2(s, os.path.join(dst, item))


# keep is a list which should be kept, others will be removed.
def unzip(keep=None):
    unzip_dir(STAGE_DIR, OUTPUT_DIR)
    path = os.path.join(OUTPUT_DIR, 'Release')
    if os.path.isdir(path):
        copy_tree(path, OUTPUT_DIR)
        shutil.rmtree(path)

    del_by_exts(OUTPUT_DIR)

    if keep is not None:
        for f in os.listdir(OUTPUT_DIR):
            if f not in keep:
                delete(os.path.join(OUTPUT_DIR, f))

    del_by_exts(STAGE_DIR)

def del_by_exts(path, exts=None):

    if os.path.isdir(path):
        default_exts = ['__MACOSX', 'Debug', 'DS_Store', 'dSYM', 'md5']
        if exts is None:
            exts = default_exts
        elif isinstance(exts, list):
            exts.extend(default_exts)
        else:
            raise ValueError('parameter exts should be list')

        for f in os.listdir(path):
            file = os.path.join(path, f)
            for e in exts:
                if file.endswith(e):
                    delete(file)

    elif os.path.isfile:
        os.remove(path)
    else:
        raise ValueError(f'{path} does\'nt exist!')


def execute_module(module_name, context=None):
    module = importlib.import_module(f'hackintosh.commands.{module_name}')
    functions = sorted(filter((lambda x: re.search(r'^_\d+', x)), dir(module)))
    for f in functions:
        func = getattr(module, f)
        sig = signature(func)

        if 'ctx' in sig.parameters.keys():
            ret = func(context)
        else:
            ret = func()

        if DEBUG:
            click.secho(ret, fg='blue', bold=True)
            click.pause('Press any key continue.')


def _execute_func(module_name, func_name, params=None):
    module = importlib.import_module(
        f'hackintosh.commands.{module_name}')
    
    func = getattr(module, f'_{func_name}')

    if params is None:
        ret = func()
    else:
        ret = func(params)

    if DEBUG:
        click.secho(ret, fg='blue', bold=True)
        click.pause('Press any key continue.')


def execute_func(module_name, func_name, params=None):
    module = importlib.import_module(f'hackintosh.commands.{module_name}')

    if f'_{func_name}' in dir(module):
        func = getattr(module, f'_{func_name}')
    else:
        r = r'^_\d+_' + re.escape(func_name)
        func = getattr(module, list(filter((lambda x: re.search(r, x)), dir(module)))[0])

    if params:
        func(params)
    else:
        func()

def clover_kext_patches(patches, output, template=None):
    if template is None:
        template = Template(open(os.path.join(
            REPO_ROOT, 'templates', 'clover_kexts_to_patch.templ')).read())

    with open(output, 'a') as f:
        for p in patches:
            content = template.substitute(p)
            f.write(content)


def download_kexts(kexts):
    
    keep_kexts = []

    for k, v in kexts.items():
        download_project(ALL_META['projects'][k])
        keep_kexts.extend(v)

    return keep_kexts


def to_num(n):
    try:
        return int(n)
    except ValueError:
        return 0