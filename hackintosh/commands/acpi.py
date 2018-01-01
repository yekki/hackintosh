from hackintosh import REPO_ROOT, LAPTOP_ROOT, LAPTOP_META, STAGE_DIR, OUTPUT_DIR, IASL, PATCHMATIC, error
from hackintosh.lib import del_by_exts
from subprocess import call

import os, glob, shutil, click


# if param dest is None, then patches will be copy to STAGE_DIR
def handle_patche_list(acpi_list, ext, dest=None):
    files = []

    for f in [f'{item}.{ext}' for item in acpi_list]:
        file = os.path.join(LAPTOP_ROOT, 'origin',
                            LAPTOP_META['acpi']['bios'], f)
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
                    file = os.path.join(REPO_ROOT, 'patches', 'static', 'patches', f)
                    if os.path.exists(file):
                        files.append(file)
                    else:
                        file = os.path.join(
                            REPO_ROOT, 'patches', 'hot', 'patches', f)
                        if os.path.exists(file):
                            files.append(file)

    if dest is None:
        dest = STAGE_DIR

    if dest == STAGE_DIR or dest == OUTPUT_DIR:
        for f in files:
            shutil.copy2(f, STAGE_DIR)
    else:
        with click.open_file(dest, 'w') as outfile:
            for f in files:
                with click.open_file(f) as infile:
                    outfile.write(infile.read())


def _1_initialize():
    if os.path.isfile(IASL):
        if os.access(IASL, os.X_OK):
            acpi_list = LAPTOP_META['acpi']['patches']['ssdt_list']
            acpi_list.append('DSDT')
            LAPTOP_META['ACPI_LIST'] = acpi_list
        else:
            error(f"{_IASL} isn't not executable.")
    else:
        error(f"{_IASL} not found, please install it firstly.")

    if os.path.isfile(PATCHMATIC):
        if not os.access(PATCHMATIC, os.X_OK):
            error(f"{PATCHMATIC} isn't not executable.")
    else:
        error(f"{PATCHMATIC} not found, please install it firstly.")

    return 'Checked compile tools successful.'


def _2_prepare_acpi_files():
    handle_patche_list(LAPTOP_META['ACPI_LIST'], 'aml')
    return 'Staged native acpi files.'


def _3_decompile():
    refs_file = os.path.join(LAPTOP_ROOT, 'patches', 'refs.txt')
    if os.path.isfile(refs_file):
        shutil.copyfile(refs_file, os.path.join(os.getcwd(), 'refs.txt'))

    call([f'{IASL} -da -dl {STAGE_DIR}/DSDT.aml {STAGE_DIR}/SSDT*.aml'], shell=True)
    del_by_exts(STAGE_DIR, exts=['aml'])

    handle_patche_list(LAPTOP_META['ACPI_LIST'], 'dsl')
    return 'Decompiled native acpi files.'


def _4_apply_dsdt_patches():
    handle_patche_list(LAPTOP_META['acpi']['patches']['dsdt'], 'txt', os.path.join(
        STAGE_DIR, 'DSDT_PATCHES.txt'), )
    call([f'{PATCHMATIC}', f'{STAGE_DIR}/DSDT.dsl',
          f'{STAGE_DIR}/DSDT_PATCHES.txt', f'{STAGE_DIR}/DSDT.dsl'])

    return 'Applied patches to DSDT.'


def _5_apply_ssdt_patches():
    keys = [x.upper() for x in LAPTOP_META['acpi']['patches']['ssdt'].keys()]
    ssdts = LAPTOP_META['acpi']['patches']['ssdt_list']

    ssdt_list = set(keys).intersection(set(ssdts))

    for ssdt in ssdt_list:
        dsl_file = f'{STAGE_DIR}/{ssdt}.dsl'
        patch_file = f'{STAGE_DIR}/{ssdt}_PATCH.txt'
        handle_patche_list(
            LAPTOP_META['acpi']['patches']['ssdt'][ssdt.lower()], 'txt', patch_file)
        call([f'{PATCHMATIC}', dsl_file, patch_file, dsl_file])

    return 'Applied patches to SSDT(s).'


def _6_check_dsl():
    files = os.listdir(STAGE_DIR)
    losts = []
    for s in LAPTOP_META['acpi']['patches']['ssdt_list']:
        if f'{s}.dsl' not in files:
            losts.append(s)

    if len(losts) > 0:
        handle_patche_list(losts, 'dsl')

    return 'Checked & appended DSL files.'


def _7_compile_acpi():
    for f in glob.glob(f'{STAGE_DIR}/*.dsl'):
        filename = os.path.basename(f).split('.')[0]
        call([f'{IASL}', '-vr', '-w1', '-p',
              f'{OUTPUT_DIR}/{filename}.aml', f'{STAGE_DIR}/{filename}.dsl'])

    handle_patche_list(LAPTOP_META['ACPI_LIST'], '.aml', OUTPUT_DIR)

    return 'Compiled all files.'


def _8_check():
    s1 = [f.replace('.aml', '') for f in os.listdir(OUTPUT_DIR)]
    s2 = set(LAPTOP_META['ACPI_LIST'])
    s3 = s2.difference(s1)

    if len(s3):
        for i in s3:
            error(f'Failed to build {i}.')

    return 'Final check passed.'
