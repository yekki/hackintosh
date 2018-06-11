from hackintosh import STAGE_DIR, PKG_ROOT, REPO_ROOT, ALL_META
from hackintosh.commands import git_clone, download_project
from hackintosh.utils import error, delete, unzip_file, download

import os, stat, glob, click, shutil


def _update_tool(zip_file, cmd_name):
    file = os.path.join(STAGE_DIR, zip_file)
    if os.path.isfile(file):
        unzip_file(file, STAGE_DIR)
        file = os.path.join(STAGE_DIR, cmd_name)
        st = os.stat(file)
        os.chmod(file, st.st_mode | stat.S_IEXEC)

        file = os.path.join(PKG_ROOT, 'bin', cmd_name)

        if os.path.exists(file): os.unlink(file)

        shutil.copy2(os.path.join(STAGE_DIR, cmd_name), os.path.join(PKG_ROOT, 'bin'))
    else:
        error(f'Lost zip file at {file}.')


def _1_ssdtPRgen():
    download('https://codeload.github.com/Piker-Alpha/ssdtPRGen.sh/zip/Beta', STAGE_DIR, filename='ssdtPRGen.sh-Beta.zip')
    ssdtPRGen_root = os.path.join(os.path.expanduser('~'), 'Library', 'ssdtPRGen')

    if os.path.isdir(ssdtPRGen_root):
        shutil.rmtree(ssdtPRGen_root)

    unzip_file(os.path.join(STAGE_DIR, 'ssdtPRGen.sh-Beta.zip'), STAGE_DIR)

    path = os.path.join(STAGE_DIR, 'ssdtPRGen.sh-Beta')

    if os.path.isdir(path):
        shutil.copytree(path, ssdtPRGen_root)
        file = os.path.join(ssdtPRGen_root, 'ssdtPRGen.sh')
        st = os.stat(path)
        os.chmod(file, st.st_mode | stat.S_IEXEC)

    return 'ssdtPRGen is updated.'


def _2_patches():
    git_clone('https://github.com/RehabMan/Laptop-DSDT-Patch.git', os.path.join(STAGE_DIR, 'patches'))
    patches_root = os.path.join(REPO_ROOT, 'patches', 'static', 'patches')

    delete(patches_root, keep=True)

    for file in glob.glob(f"{os.path.join(STAGE_DIR, 'patches')}/**/*.txt"):
        shutil.copy2(file, patches_root)

    click.echo('ACPI static patches are updated.')

    git_clone('https://github.com/RehabMan/OS-X-Clover-Laptop-Config', os.path.join(STAGE_DIR, 'config'))

    path = os.path.join(REPO_ROOT, 'patches', 'hot', 'patches')
    shutil.rmtree(path)
    shutil.copytree(os.path.join(STAGE_DIR, 'config', 'hotpatch'), path)

    path = os.path.join(REPO_ROOT, 'patches', 'hot', 'config')

    delete(path, exts=['.plist'])

    for file in glob.glob(f"{os.path.join(STAGE_DIR, 'config')}/*.plist"):
        shutil.copy2(file, path)

    click.echo('ACPI hot patches are updated.')
    return 'ACPI patches are updated.'


def _3_iasl():
    filename = download_project(ALL_META['projects']['acpica'])
    _update_tool(filename, 'iasl')
    return 'iasl is updated.'


def _4_patchmatic():
    filename = download_project(ALL_META['projects']['os-x-maciasl-patchmatic'])
    _update_tool(filename, 'patchmatic')
    return 'patchmatic is updated.'
