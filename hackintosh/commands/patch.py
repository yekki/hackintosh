from hackintosh import ALL_META, STAGE_DIR, OUTPUT_DIR, ENV
from hackintosh.commands import clover_kext_patches, download_kexts, git_clone, unzip, install_kexts, download_project
from hackintosh.utils import error
from subprocess import call, check_call, CalledProcessError
from click import echo

import os, shutil


def _brightness_control():

    git_clone('https://github.com/RehabMan/HP-ProBook-4x30s-DSDT-Patch', 'probook.git')
    git_clone('https://github.com/RehabMan/OS-X-Clover-Laptop-Config.git', 'guide.git')

    pnlf = os.path.join(STAGE_DIR, 'guide.git', 'build', 'SSDT-PNLF.aml')

    if not os.path.exists(pnlf):
        call(['make'], cwd=f'{STAGE_DIR}/guide.git', env=ENV)

    if os.path.exists(pnlf):
        shutil.copy2(pnlf, OUTPUT_DIR)
    else:
        error(f'Failed to find ACPI file at {pnlf}.')

    kext = os.path.join(f'{STAGE_DIR}/probook.git', 'kexts', 'AppleBacklightInjector.kext')

    if os.path.exists(kext):
        shutil.copytree(kext, os.path.join(OUTPUT_DIR, 'AppleBacklightInjector.kext'))
    else:
        error(f'Failed to find kext at {kext}.')

    clover_kext_patches(ALL_META['patches']['brightness_control']['clover']['kexts_to_patch'],
                        os.path.join(OUTPUT_DIR, 'patch.plist'))

    return 'All widgets for patch are prepared.'


def _system():
    kexts = download_kexts(ALL_META['patches']['system']['kexts'])

    if kexts is not None:
        unzip(kexts)

    clover_kext_patches(ALL_META['patches']['system']['clover']['kexts_to_patch'],
                        os.path.join(OUTPUT_DIR, 'patch.plist'))

    return 'All widgets for patch are prepared.'

def _voodoops():
    echo("Downloading VoodooPS2 now...")
    download_project(ALL_META['projects']['os-x-voodoo-ps2-controller'])
    unzip(['VoodooPS2Daemon', 'org.rehabman.voodoo.driver.Daemon.plist', 'VoodooPS2Controller.kext'])
    echo("VoodooPS2 downloaded, installing now...")

    install_kexts(os.path.join(OUTPUT_DIR, 'VoodooPS2Controller.kext'))

    try:
        check_call(['/usr/bin/sudo', 'cp', f'{OUTPUT_DIR}/VoodooPS2Daemon', '/usr/bin/'])
        echo('VoodooPS2Daemon is installed.')
    except CalledProcessError:
        error('Failed to install VoodooPS2 widgets: VoodooPS2Daemon')

    try:
        check_call(['/usr/bin/sudo', 'cp', f'{OUTPUT_DIR}/org.rehabman.voodoo.driver.Daemon.plist',
                    '/Library/LaunchDaemons/'])
        echo('org.rehabman.voodoo.driver.Daemon.plist is installed.')
    except CalledProcessError:
        error('Failed to install VoodooPS2 widgets: org.rehabman.voodoo.driver.Daemon.plist')