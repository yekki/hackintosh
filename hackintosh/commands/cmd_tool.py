from hackintosh.utils import execute

import importlib

import click


@click.command()
@click.option('-a', '--all', is_flag=True, help='Update all tools & patches.')
@click.option('-t', '--tool', type=click.Choice(['iasl', 'pathmatic', 'patches', 'ssdtPRgen']),
              help='choose the tool which will be updated.')
def cli(all, tool):
    if all:
        execute('app')
    else:
        if tool:
            module = importlib.import_module(f'hackintosh.app')
            getattr(module, f'update_{tool}')()

