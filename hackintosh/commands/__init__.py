from hackintosh import *
from inspect import signature
from distutils.dir_util import copy_tree

import importlib, re, shutil


def cleanup():
    if os.path.join(os.getcwd(), 'hackintosh') == Path.PKG_ROOT:
        cleanup_dirs(Path.STAGE_DIR, Path.OUTPUT_DIR, rmdir=True)
    else:
        cleanup_dirs(Path.STAGE_DIR, Path.OUTPUT_DIR)

    delete_files(os.path.join(os.getcwd(), 'refs.txt'))


def unzip():
    unzip_dir(Path.STAGE_DIR, Path.OUTPUT_DIR)
    path = os.path.join(Path.OUTPUT_DIR, 'Release')
    if os.path.isdir(path):
        copy_tree(path, Path.OUTPUT_DIR)
        shutil.rmtree(path)

    for f in ('AppleALC.kext.dSYM', '__MACOSX', 'Debug', 'HWMonitor.app',
              'FakeSMC_ACPISensors.kext', 'FakeSMC_CPUSensors.kext',
              'FakeSMC_GPUSensors.kext', 'FakeSMC_LPCSensors.kext'):
        path = os.path.join(Path.OUTPUT_DIR, f)
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)


def execute_module(module_name, context=None):
    module = importlib.import_module(f'hackintosh.commands.{module_name}_impl')
    functions = sorted(filter((lambda x: re.search(r'^_\d+', x)), dir(module)))
    for f in functions:
        func = getattr(module, f)
        sig = signature(func)

        if 'ctx' in sig.parameters.keys():
            func(context)
        else:
            func()
