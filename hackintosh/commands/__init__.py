# -*- coding: utf-8 -*-

import os, shutil, click, json

from click import echo
from subprocess import CalledProcessError, check_call, call
from functools import wraps

from git import Repo

from hackintosh.parser import parse
from hackintosh.utils import error, delete, download, unzip_dir, copy_dir
from hackintosh import OUTPUT_DIR, STAGE_DIR, REPO_ROOT, ALL_META, CLIENT_SETTINGS_FILE
from string import Template
from inspect import signature
from importlib import import_module

import re

__all__ = ['execute_module', 'execute_func', 'save_conf', 'install_kexts', 'cleanup', 'download_kexts', 'git_clone',
           'download_project', 'unzip', 'clover_kext_patches', 'print_project', 'rebuild_cache']


def rebuild_cache():
    cmd = ['sudo', '/usr/sbin/kextcache', '-i', '/']
    call(cmd)


def execute_module(module_name, context=None, debug=False):
    module = import_module(f'hackintosh.commands.{module_name}')
    functions = sorted(filter((lambda x: re.search(r'^_\d+', x)), dir(module)))
    for f in functions:
        func = getattr(module, f)
        sig = signature(func)

        if 'ctx' in sig.parameters.keys():
            ret = func(context)
        else:
            ret = func()

        if debug:
            click.secho(ret, fg='blue', bold=True)
            click.pause('Press any key continue.')


def execute_func(module_name, func_name, params=None):
    module = import_module(f'hackintosh.commands.{module_name}')

    if f'_{func_name}' in dir(module):
        func = getattr(module, f'_{func_name}')
    else:
        r = r'^_\d+_' + re.escape(func_name)
        func = getattr(module, list(filter((lambda x: re.search(r, x)), dir(module)))[0])

    if params:
        func(params)
    else:
        func()


def save_conf(data):
    with open(CLIENT_SETTINGS_FILE, 'w', encoding='utf8') as f:
        f.write(json.dumps(data,
                           indent=4, sort_keys=True,
                           separators=(',', ': '), ensure_ascii=False))


def install_kexts(kexts):
    try:
        if type(kexts) is list:
            for k in kexts:
                check_call(f'sudo cp -R {k} /Library/Extensions')
        else:
            check_call(f'sudo cp -R {kexts} /Library/Extensions')

        echo('Rebuilding caches and fix permissions.')
        check_call(f'sudo touch /System/Library/Extensions && sudo kextcache -u /')
        echo('kext(s) is installed.')
    except CalledProcessError:
        error(f'Failed to install kext:{kexts}')


def cleanup(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        delete(OUTPUT_DIR)
        delete(STAGE_DIR)
        delete(os.path.join(os.getcwd(), 'refs.txt'))
        ret = func(*args, **kwargs)
        return ret

    return wrapper


def download_kexts(kexts):
    keep_kexts = []
    for k, v in kexts.items():
        download_project(ALL_META['projects'][k])
        keep_kexts.extend(v)

    return keep_kexts


def git_clone(url, dir):
    path = os.path.join(STAGE_DIR, dir)

    if os.path.exists(path):
        delete(path)
    else:
        os.mkdir(path)
        Repo.clone_from(url, path)


def download_project(meta):
    p = parse(meta)
    if p:
        url = p.get('url', '')
        if url.startswith('/'):
            copy_dir(url, OUTPUT_DIR)
            return p['name']
        else:
            return download(p['url'], STAGE_DIR, p['name'])
    else:
        error(f'Failed to parse project meta:{meta}')


def unzip(kexts, to_dir=None):
    unzip_dir(STAGE_DIR, STAGE_DIR)
    from_dirs = [os.path.join(STAGE_DIR, 'Release'), STAGE_DIR]

    if to_dir:
        to_dir = os.path.join(OUTPUT_DIR, to_dir)
        if not os.path.exists(to_dir): os.mkdir(to_dir)
    else:
        to_dir = OUTPUT_DIR

    for f in from_dirs:
        if os.path.isdir(f):
            for k in os.listdir(f):
                if (kexts and k in kexts):
                    shutil.move(os.path.join(f, k), os.path.join(OUTPUT_DIR, to_dir))

    # pass list() means clean default files set by CMD_CONST
    delete(to_dir, list())


def clover_kext_patches(patches, output, template=None):
    if template is None:
        template = Template(open(os.path.join(
            REPO_ROOT, 'templates', 'clover_kexts_to_patch.templ')).read())

    with open(output, 'a') as f:
        for p in patches:
            content = template.substitute(p)
            f.write(content)


def print_project(meta, kexts=None, show_update_date=False):
    if show_update_date:
        m = parse(meta)
        s = f", Updated:{m.get('updated_at', 'None')}"
    else:
        s = ""

    click.echo(f"- Name:{meta['project']}, Author: {meta['account']}{s}")

    if kexts:
        click.secho(f'  {kexts}', fg='green')


if __name__ == '__main__':
    pass
