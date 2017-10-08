from hackintosh import PKG_ROOT, REPO_ROOT, LAPTOP_ROOT, LAPTOP_META, STAGE_DIR, OUTPUT_DIR
from hackintosh.lib import copy_dir, delete, cust_acpi_patches, error, message
from subprocess import call

import os, glob, shutil

## iasl61 come from MaciASL
_IASL = os.path.join(PKG_ROOT, 'bin', 'iasl61')
_PATCHMATIC = os.path.join(PKG_ROOT, 'bin', 'patchmatic')


def _apply_patch(patch_file, patch_list):
    with open(patch_file, 'w') as outfile:
        for p in patch_list:
            # check laptop specific patch first, if not found, check common patch repo, if not found, check system patch repo.
            path = os.path.join(f'{LAPTOP_ROOT}', 'patches', f'{p}.txt')
            if not os.path.exists(path):
                path = os.path.join(f'{REPO_ROOT}', 'common', 'patches', f'{p}.txt')
                if not os.path.exists(path):
                    path = os.path.join(f'{REPO_ROOT}', 'patches', f'{p}.txt')

            if os.path.isfile(path):
                with open(path) as infile:
                    outfile.write(infile.read())
            else:
                error(f'Lost patch: {path}.')


def _1_initialize():
    if os.path.isfile(_IASL):
        acpi_list = LAPTOP_META['acpi']['patches']['ssdt_list']
        acpi_list.append('DSDT')
        LAPTOP_META['ACPI_LIST'] = acpi_list
    else:
        error('Please install iasl commandline tools firstly.')


def _2_prepare_acpi_files():
    native_acpi_dir = os.path.join(LAPTOP_ROOT, 'origin', LAPTOP_META['acpi']['bios'])
    copy_dir(native_acpi_dir, STAGE_DIR, [f'{item}.aml' for item in LAPTOP_META['ACPI_LIST']])
    cust_acpi_patches('.dsl', LAPTOP_META['ACPI_LIST'], STAGE_DIR)


def _3_decompile():
    refs_file = os.path.join(LAPTOP_ROOT, 'patches', 'refs.txt')
    if os.path.isfile(refs_file):
        shutil.copyfile(refs_file, os.path.join(os.getcwd(), 'refs.txt'))

    call([f'{_IASL} -da -dl {STAGE_DIR}/DSDT.aml {STAGE_DIR}/SSDT*.aml'], shell=True)
    delete(STAGE_DIR, ext='aml', only_files=True)
    copy_dir(f'{LAPTOP_ROOT}/patches', STAGE_DIR, [f'{item}.dsl' for item in LAPTOP_META['ACPI_LIST']])


def _4_apply_dsdt_patches():
    _apply_patch(f'{STAGE_DIR}/DSDT_PATCHES.txt', LAPTOP_META['acpi']['patches']['dsdt'])
    call([f'{_PATCHMATIC}', f'{STAGE_DIR}/DSDT.dsl', f'{STAGE_DIR}/DSDT_PATCHES.txt', f'{STAGE_DIR}/DSDT.dsl'])


def _5_apply_ssdt_patches():
    keys = [x.upper() for x in LAPTOP_META['acpi']['patches']['ssdt'].keys()]
    ssdts = LAPTOP_META['acpi']['patches']['ssdt_list']

    ssdt_list = set(keys).intersection(set(ssdts))

    for ssdt in ssdt_list:
        dsl_file = f'{STAGE_DIR}/{ssdt}.dsl'
        patch_file = f'{STAGE_DIR}/{ssdt}_PATCH.txt'
        _apply_patch(patch_file, LAPTOP_META['acpi']['patches']['ssdt'][ssdt.lower()])
        call([f'{_PATCHMATIC}', dsl_file, patch_file, dsl_file])


def _6_compile_acpi():
    for f in glob.glob(f'{STAGE_DIR}/*.dsl'):
        filename = os.path.basename(f).split('.')[0]
        call([f'{_IASL}', '-vr', '-w1', '-p', f'{OUTPUT_DIR}/{filename}.aml', f'{STAGE_DIR}/{filename}.dsl'])

    cust_acpi_patches('.aml', LAPTOP_META['ACPI_LIST'], OUTPUT_DIR)


def _7_check():
    s1 = [f.replace('.aml', '') for f in os.listdir(OUTPUT_DIR)]
    s2 = set(LAPTOP_META['ACPI_LIST'])
    s3 = s2.difference(s1)

    if len(s3):
        for i in s3:
            error(f'Failed to build {i}.')
    else:
        message('Finished.')
