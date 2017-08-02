from hackintosh import PKG_ROOT, REPO_ROOT, LAPTOP_ROOT, LAPTOP_META
from hackintosh.lib import copy_dir, run, del_dir

import os, glob, logging, shutil

_IASL = os.path.join(PKG_ROOT, 'bin', 'iasl')
_PATCHMATIC = os.path.join(PKG_ROOT, 'bin', 'patchmatic')


def _apply_patch(patch_file, patch_list):
    """
    To fetch patch files according patch-name list and combine them in one patch file.
    
    :param patch_file: the patch file which contains merged patches from patch_list
    :param patch_list: patch name list
    :return: 
    """
    with open(patch_file, 'w') as outfile:
        for p in patch_list:
            patch = f'{REPO_ROOT}/patches/{p}.txt'

            # check whether patch in system repo, if not, check laptop's patch
            if not os.path.isfile(patch):
                patch = f'{LAPTOP_ROOT}/patches/{p}.txt'

            if os.path.isfile(patch):
                with open(patch) as infile:
                    outfile.write(infile.read())
            else:
                logging.info(f'lost patch at {patch}')


def _1_initialize():
    if os.path.isfile(os.path.join(PKG_ROOT, 'bin', 'iasl')):
        acpi_list = LAPTOP_META['acpi']['patches']['ssdt']['ssdt_names']
        acpi_list.append('DSDT')
        LAPTOP_META['ACPI_LIST'] = acpi_list
    else:
        logging.critical('please install iasl commandline tools firstly.')
        exit(-1)


def _2_prepare_acpi_files():
    native_acpi_dir = os.path.join(LAPTOP_ROOT, 'origin', LAPTOP_META['acpi']['bios'])
    copy_dir(native_acpi_dir, 'stage', [f'{item}.aml' for item in LAPTOP_META['ACPI_LIST']])


def _3_decompile():
    refs_file = os.path.join(LAPTOP_ROOT, 'patches', 'refs.txt')
    if os.path.isfile(refs_file):
        shutil.copyfile(refs_file, os.path.join(os.getcwd(), 'refs.txt'))

    cmd = [f'{_IASL} -da -dl ./stage/DSDT.aml ./stage/SSDT*.aml']
    run(cmd, msg='decompiled %d .aml files' % len(LAPTOP_META['ACPI_LIST']), ignore_error=True)
    del_dir('stage', 'aml')
    copy_dir(f'{LAPTOP_ROOT}/patches', 'stage',
             [f'{item}.dsl' for item in LAPTOP_META['ACPI_LIST']])


def _4_apply_dsdt_patches():
    _apply_patch('./stage/DSDT_PATCHES.txt', LAPTOP_META['acpi']['patches']['dsdt'])
    cmd = [f'{_PATCHMATIC} ./stage/DSDT.dsl ./stage/DSDT_PATCHES.txt ./stage/DSDT.dsl']
    run(cmd, ignore_error=True)


def _5_apply_ssdt_patches():
    keys = [x.upper() for x in LAPTOP_META['acpi']['patches']['ssdt'].keys()]
    ssdts = LAPTOP_META['acpi']['patches']['ssdt']['ssdt_names']

    ssdt_list = set(keys).intersection(set(ssdts))

    for ssdt in ssdt_list:
        dsl_file = f'./stage/{ssdt}.dsl'
        patch_file = f'./stage/{ssdt}_PATCH.txt'
        _apply_patch(patch_file, LAPTOP_META['acpi']['patches']['ssdt'][ssdt.lower()])

        cmd = [f'{_PATCHMATIC} {dsl_file} {patch_file} {dsl_file}']
        run(cmd, ignore_error=True)


def _6_compile_acpi():
    for f in glob.glob('./stage/*.dsl'):
        filename = os.path.basename(f).split('.')[0]
        cmd = [f'{_IASL} -vr -w1 -p ./output/{filename}.aml ./stage/{filename}.dsl']
        run(cmd, ignore_error=True)


def _7_customize():
    copy_dir(f'{LAPTOP_ROOT}/patches', './output', [f'{item}.aml' for item in LAPTOP_META['ACPI_LIST']])
