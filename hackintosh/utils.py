# -*- coding: utf-8 -*-

import os, shutil, click, requests, cgi, json
from subprocess import check_call, check_output, call
from zipfile import ZipFile

__all__ = ['copy_dir', 'error', 'to_num', 'save_conf', 'cleanup_by_exts', 'delete', 'download', 'unzip_dir', 'unzip_file']


def check_root():
    if os.geteuid() != 0: error('Please execute this command with sudo.')

def _run(cmd, file=None, ignore_error=False):
    if file is None:
        if ignore_error:
            call(cmd)
        else:
            check_call(cmd)
    else:
        with open(file, 'wb') as f:
            f.write(check_output(cmd))


def copy_dir(src, dest, overwrite=True, exclude=None):
    if os.path.isdir(dest) and os.path.isdir(src):
        if os.path.isdir(src):
            files = (set(os.listdir(src)) - exclude) if exclude else os.listdir(src)
            basedir = os.path.dirname(src)
            for f in files:
                s = os.path.join(basedir, f)
                cmd = ['cp', '-rf', f'{s}', f'{dest}']
                if os.path.exists(os.path.join(dest, f)):
                    if overwrite: call(cmd)
                else:
                    call(cmd)
        elif os.path.isfile(src):
            cmd = ['cp', '-rf', f'{src}', f'{dest}']
            if os.path.exists(src):
                if overwrite: call(cmd)
            else:
                call(cmd)
    else:
        raise ValueError(f'Make sure {src} and {dest} are directories.')


def error(msg, fg='red'):
    click.secho(msg, fg=fg)
    exit(-1)


def to_num(n):
    try:
        return int(n)
    except ValueError:
        return 0


def save_conf(file, data):
    with open(file, 'w', encoding='utf8') as f:
        f.write(json.dumps(data,
                           indent=4, sort_keys=True,
                           separators=(',', ': '), ensure_ascii=False))


def cleanup_by_exts(dir, exts=None):
    ext_list = ['__MACOSX', 'Debug', 'DS_Store', 'dSYM', 'md5']

    if exts: ext_list.extend(exts)

    for f in os.listdir(dir):
        file = os.path.join(dir, f)
        for e in ext_list:
            if file.endswith(e) and os.path.isfile(file):
                delete(file)


def delete(path, exts=None, keep=True):
    if os.path.isdir(path):

        if exts is None:
            shutil.rmtree(path)
            if keep: os.mkdir(path)
        else:
            cleanup_by_exts(path, exts)
    elif os.path.isfile(path):
        os.remove(path)
    elif keep:
        os.mkdir(path)


def download(url, folder, filename=None):
    r = requests.get(url, stream=True)

    if not filename:
        if "Content-Disposition" in r.headers:
            _, params = cgi.parse_header(r.headers["Content-Disposition"])
            filename = params["filename"]
        else:
            filename = url.split("/")[-1]

    try:
        total_length = int(r.headers.get('content-length'))
    except TypeError:
        error('Please try again.')

    # change filename to void conflict with each other
    if filename[0].isdigit(): filename = f'{str(total_length)}.{filename}'

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


def unzip_file(file, dest_dir):
    zip_ref = ZipFile(file)
    zip_ref.extractall(dest_dir)
    zip_ref.close()


def unzip_dir(from_dir, to_dir, ext='.zip'):
    for item in os.listdir(from_dir):
        if item.endswith(ext):
            unzip_file(os.path.join(from_dir, item), to_dir)


if __name__ == '__main__':
    # copy('/Users/gniu/a', '/Users/gniu/b')
    delete('/Users/gniu/b')
