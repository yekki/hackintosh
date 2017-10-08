from hackintosh import PKG_ROOT, REPO_ROOT, LAPTOP_ROOT, LAPTOP_META, STAGE_DIR, OUTPUT_DIR, ALL_META
from hackintosh.lib import delete, error, message
from subprocess import call

import os, glob, shutil

## iasl61 come from MaciASL
_IASL = os.path.join(PKG_ROOT, 'bin', ALL_META['tools']['iasl'])
_PATCHMATIC = os.path.join(PKG_ROOT, 'bin', ALL_META['tools']['patchmatic'])


# if param dest is None, then patches will be copy to STAGE_DIR
def handle_patche_list(acpi_list, ext, dest=None):
    files = []

    for f in [f'{item}.{ext}' for item in acpi_list]:
        file = os.path.join(LAPTOP_ROOT, 'origin', LAPTOP_META['acpi']['bios'], f)
        if os.path.exists(file):
            files.append(file)
        else:
            file = os.path.join(LAPTOP_ROOT, 'patches', f)
            if os.path.exists(file):
                files.append(file)
            else:
                file = os.path.join(REPO_ROOT, 'common', 'patches', f)
                if os.path.exists(file):
                    files.append(file)
                else:
                    file = os.path.join(REPO_ROOT, 'patches', 'static', f)
                    if os.path.exists(file):
                        files.append(file)
                    else:
                        file = os.path.join(REPO_ROOT, 'patches', 'hot', 'hotpatch', f)
                        if os.path.exists(file):
                            files.append(file)

    if dest is None: dest = STAGE_DIR

    if dest == STAGE_DIR or dest == OUTPUT_DIR:
        for f in files:
            shutil.copy2(f, STAGE_DIR)
    else:
        with open(dest, 'w') as outfile:
            for f in files:
                with open(f) as infile:
                    outfile.write(infile.read())


def _1_initialize():
    if os.path.isfile(_IASL):
        if os.access(_IASL, os.X_OK):
            acpi_list = LAPTOP_META['acpi']['patches']['ssdt_list']
            acpi_list.append('DSDT')
            LAPTOP_META['ACPI_LIST'] = acpi_list
        else:
            error(f"{_IASL} isn't not executable.")
    else:
        error(f"{_IASL} not found, please install it firstly.")

    if os.path.isfile(_PATCHMATIC):
        if not os.access(_PATCHMATIC, os.X_OK):
            error(f"{_PATCHMATIC} isn't not executable.")
    else:
        error(f"{_PATCHMATIC} not found, please install it firstly.")


def _2_prepare_acpi_files():
    handle_patche_list(LAPTOP_META['ACPI_LIST'], 'aml')


def _3_decompile():
    refs_file = os.path.join(LAPTOP_ROOT, 'patches', 'refs.txt')
    if os.path.isfile(refs_file):
        shutil.copyfile(refs_file, os.path.join(os.getcwd(), 'refs.txt'))

    call([f'{_IASL} -da -dl {STAGE_DIR}/DSDT.aml {STAGE_DIR}/SSDT*.aml'], shell=True)
    delete(STAGE_DIR, ext='aml', only_files=True)

    handle_patche_list(LAPTOP_META['ACPI_LIST'], 'dsl')


def _4_apply_dsdt_patches():
    handle_patche_list(LAPTOP_META['acpi']['patches']['dsdt'], 'txt', os.path.join(STAGE_DIR, 'DSDT_PATCHES.txt'), )
    call([f'{_PATCHMATIC}', f'{STAGE_DIR}/DSDT.dsl', f'{STAGE_DIR}/DSDT_PATCHES.txt', f'{STAGE_DIR}/DSDT.dsl'])


def _5_apply_ssdt_patches():
    keys = [x.upper() for x in LAPTOP_META['acpi']['patches']['ssdt'].keys()]
    ssdts = LAPTOP_META['acpi']['patches']['ssdt_list']

    ssdt_list = set(keys).intersection(set(ssdts))

    for ssdt in ssdt_list:
        dsl_file = f'{STAGE_DIR}/{ssdt}.dsl'
        patch_file = f'{STAGE_DIR}/{ssdt}_PATCH.txt'
        handle_patche_list(LAPTOP_META['acpi']['patches']['ssdt'][ssdt.lower()], 'txt', patch_file)
        call([f'{_PATCHMATIC}', dsl_file, patch_file, dsl_file])


def _6_compile_acpi():
    for f in glob.glob(f'{STAGE_DIR}/*.dsl'):
        filename = os.path.basename(f).split('.')[0]
        call([f'{_IASL}', '-vr', '-w1', '-p', f'{OUTPUT_DIR}/{filename}.aml', f'{STAGE_DIR}/{filename}.dsl'])

    handle_patche_list(LAPTOP_META['ACPI_LIST'], '.aml', OUTPUT_DIR)


def _7_check():
    s1 = [f.replace('.aml', '') for f in os.listdir(OUTPUT_DIR)]
    s2 = set(LAPTOP_META['ACPI_LIST'])
    s3 = s2.difference(s1)

    if len(s3):
        for i in s3:
            error(f'Failed to build {i}.')
    else:
        message('Finished.')
