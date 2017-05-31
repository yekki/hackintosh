from shutil import copyfile
from hackintosh.utils import dir_copy, dir_del, run, Path

import hackintosh.logger as logger
import os, glob

_IASL = os.path.join(Path.PKG_ROOT, 'bin', 'iasl')
_PATCHMATIC = os.path.join(Path.PKG_ROOT, 'bin', 'patchmatic')


def _apply_patch(ctx, patch_file, patch_list):
    with open(patch_file, 'w') as outfile:
        for p in patch_list:
            patch = f'{ctx.repo_path}/patches/{p}.txt'

            # check whether patch in system repo, if not, check laptop's patch
            if not os.path.isfile(patch):
                patch = f'{ctx.laptop_path}/patches/{p}.txt'

            if os.path.isfile(patch):
                with open(patch) as infile:
                    outfile.write(infile.read())
            else:
                logger.info(f'lost patch at {patch}')


def _1_initialize(ctx):
    if os.path.isfile(os.path.join(Path.PKG_ROOT, 'bin', 'iasl')):
        acpi_list = ctx.laptop['acpi']['patches']['ssdt']['ssdt_names']
        acpi_list.append('DSDT')
        ctx.laptop['ACPI_LIST'] = acpi_list
    else:
        logger.critical('please install iasl commandline tools firstly.')


def _2_prepare_acpi_files(ctx):
    native_acpi_dir = os.path.join(ctx.laptop_path, 'origin', ctx.laptop['acpi']['bios'])
    dir_copy(native_acpi_dir, 'stage', [f'{item}.aml' for item in ctx.laptop['ACPI_LIST']])


def _3_decompile(ctx):
    refs_file = os.path.join(ctx.laptop_path, 'patches', 'refs.txt')
    if os.path.isfile(refs_file):
        copyfile(refs_file, os.path.join(os.getcwd(), 'refs.txt'))

    cmd = [f'{_IASL} -da -dl ./stage/DSDT.aml ./stage/SSDT*.aml']
    run(cmd, msg='decompiled %d .aml files' % len(ctx.laptop['ACPI_LIST']), ignore_error=True)
    dir_del('stage', 'aml')
    dir_copy(f'{ctx.laptop_path}/patches', 'stage',
             [f'{item}.dsl' for item in ctx.laptop['ACPI_LIST']])


def _4_apply_dsdt_patches(ctx):
    _apply_patch(ctx, './stage/DSDT_PATCHES.txt', ctx.laptop['acpi']['patches']['dsdt'])
    cmd = [f'{_PATCHMATIC} ./stage/DSDT.dsl ./stage/DSDT_PATCHES.txt ./stage/DSDT.dsl']
    run(cmd, ignore_error=True)


def _5_apply_ssdt_patches(ctx):
    keys = [x.upper() for x in ctx.laptop['acpi']['patches']['ssdt'].keys()]
    ssdts = ctx.laptop['acpi']['patches']['ssdt']['ssdt_names']

    ssdt_list = set(keys).intersection(set(ssdts))

    for ssdt in ssdt_list:
        dsl_file = f'./stage/{ssdt}.dsl'
        patch_file = f'./stage/{ssdt}_PATCH.txt'
        _apply_patch(ctx, patch_file, ctx.laptop['acpi']['patches']['ssdt'][ssdt.lower()])

        cmd = [f'{_PATCHMATIC} {dsl_file} {patch_file} {dsl_file}']
        run(cmd, ignore_error=True)


def _6_compile_acpi(ctx):
    for f in glob.glob('./stage/*.dsl'):
        filename = os.path.basename(f).split('.')[0]
        cmd = [f'{_IASL} -vr -w1 -p ./output/{filename}.aml ./stage/{filename}.dsl']
        run(cmd, ignore_error=True)


def _7_customize(ctx):
    dir_copy(f'{ctx.laptop_path}/patches', './output', [f'{item}.aml' for item in ctx.laptop['ACPI_LIST']])
