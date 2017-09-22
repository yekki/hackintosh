from hackintosh import STAGE_DIR, PKG_ROOT, REPO_ROOT
from hackintosh.lib import unzip_file, download, download_rehabman, delete
from subprocess import call
import os, stat, shutil, logging, glob


def _update_tool(zip_file, cmd_name):
    file = os.path.join(STAGE_DIR, zip_file)

    if os.path.isfile(file):
        unzip_file(file, STAGE_DIR)
        file = os.path.join(STAGE_DIR, cmd_name)

        st = os.stat(file)
        os.chmod(file, st.st_mode | stat.S_IEXEC)

        file = os.path.join(PKG_ROOT, 'bin', cmd_name)

        if os.path.isfile(file):
            os.unlink(file)

        shutil.copy2(os.path.join(STAGE_DIR, cmd_name), os.path.join(PKG_ROOT, 'bin'))
    else:
        logging.error(f'lost zip file at {file}')


def _1_ssdtPRgen():
    download('https://codeload.github.com/Piker-Alpha/ssdtPRGen.sh/zip/Beta', folder=STAGE_DIR,
             filename='ssdtPRGen.sh-Beta.zip')
    ssdtPRGen_root = os.path.join(os.path.expanduser('~'), 'Library', 'ssdtPRGen')

    if os.path.isdir(ssdtPRGen_root):
        shutil.rmtree(ssdtPRGen_root)

    unzip_file(os.path.join(STAGE_DIR, 'ssdtPRGen.sh-Beta.zip'), STAGE_DIR)

    path = os.path.join(STAGE_DIR, 'ssdtPRGen.sh-Beta')

    if os.path.isdir(path):
        shutil.copytree(path, ssdtPRGen_root)

    logging.info('updated ssdtPRGen')


def _2_patches():
    call([f'git clone https://github.com/RehabMan/Laptop-DSDT-Patch.git {STAGE_DIR}/patches'], shell=True)

    patches_root = os.path.join(REPO_ROOT, 'patches')

    delete(patches_root, only_files=True)

    for file in glob.glob(f"{os.path.join(STAGE_DIR, 'patches')}/**/*.txt"):
        shutil.copy2(file, patches_root)

    logging.info('updated acpi patches')


def _3_iasl():
    filename = download_rehabman('acpica')
    _update_tool(filename, 'iasl')
    logging.info('updated iasl')


def _4_patchmatic():
    filename = download_rehabman('os-x-maciasl-patchmatic', filter='patchmatic')
    _update_tool(filename, 'patchmatic')
    logging.info('updated patchmatic')
