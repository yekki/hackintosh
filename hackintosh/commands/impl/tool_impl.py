from hackintosh import *


def _update_tool(zip_file, cmd_name):
    file = os.path.join(Path.STAGE_DIR, zip_file)

    if os.path.isfile(file):
        unzip_file(file, Path.STAGE_DIR)
        file = os.path.join(Path.STAGE_DIR, cmd_name)

        st = os.stat(file)
        os.chmod(file, st.st_mode | stat.S_IEXEC)

        file = os.path.join(Path.PKG_ROOT, 'bin', cmd_name)

        if os.path.isfile(file):
            os.unlink(file)

        shutil.copy2(os.path.join(Path.STAGE_DIR, cmd_name), os.path.join(Path.PKG_ROOT, 'bin'))
    else:
        error(f'lost zip file at {file}')


def _1_ssdtPRgen():
    download('https://codeload.github.com/Piker-Alpha/ssdtPRGen.sh/zip/Beta', filename='ssdtPRGen.sh-Beta.zip')
    ssdtPRGen_root = os.path.join(os.path.expanduser('~'), 'Library', 'ssdtPRGen')

    if os.path.isdir(ssdtPRGen_root):
        shutil.rmtree(ssdtPRGen_root)

    unzip_file(os.path.join(Path.STAGE_DIR, 'ssdtPRGen.sh-Beta.zip'), Path.STAGE_DIR)

    path = os.path.join(Path.STAGE_DIR, 'ssdtPRGen.sh-Beta')

    if os.path.isdir(path):
        shutil.copytree(path, ssdtPRGen_root)

    info('updated ssdtPRGen')


def _2_patches():
    cmd = [f'git clone https://github.com/RehabMan/Laptop-DSDT-Patch.git {Path.STAGE_DIR}/patches']
    run(cmd, show_out=False)

    patches_root = os.path.join(Path.PKG_REPO, 'patches')

    delete_files(patches_root)

    for file in glob.glob(f"{os.path.join(Path.STAGE_DIR, 'patches')}/**/*.txt"):
        shutil.copy2(file, patches_root)

    info('updated acpi patches')


def _3_iasl():
    filename = download_rehabman('acpica')
    _update_tool(filename, 'iasl')
    info('updated iasl')


def _4_patchmatic():
    filename = download_rehabman('os-x-maciasl-patchmatic', filter='patchmatic')
    _update_tool(filename, 'patchmatic')
    info('updated patchmatic')
