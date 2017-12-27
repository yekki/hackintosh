from hackintosh import ALL_META, STAGE_DIR, OUTPUT_DIR, ENV, error
from hackintosh.lib import clover_kext_patches, download_kexts, unzip
from subprocess import call

import os, shutil


def _brightness_control():
    cmd = ['git', 'clone', 'https://github.com/RehabMan/HP-ProBook-4x30s-DSDT-Patch', f'{STAGE_DIR}/probook.git']
    if not os.path.exists(f'{STAGE_DIR}/probook.git'):
        call(cmd)

    cmd = ['git', 'clone', 'https://github.com/RehabMan/OS-X-Clover-Laptop-Config.git', f'{STAGE_DIR}/guide.git']
    if not os.path.exists(f'{STAGE_DIR}/guide.git'):
        call(cmd)

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


def _system():
    kexts = download_kexts(ALL_META['patches']['system']['kexts'])

    if kexts is not None:
        unzip(kexts)

    clover_kext_patches(ALL_META['patches']['system']['clover']['kexts_to_patch'],
                        os.path.join(OUTPUT_DIR, 'patch.plist'))