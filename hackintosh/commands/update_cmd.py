from hackintosh.lib import execute_module, cleanup, import_module_impl
import click, re

@click.command(short_help='Update tools & patches.')
@click.option('-a', '--all', is_flag=True, help='Update all tools & patches.')
@click.option('-t', '--tool', type=click.Choice(['iasl', 'patchmatic', 'patches', 'ssdtPRgen']),
              help='Chosen the tool which will be updated.')
def cli(all, tool):
    cleanup()

    if all:
        execute_module('hackintosh.commands.update_cmd')
    else:
        if tool:
            module = import_module_impl('hackintosh.commands.update_cmd')
            r = r'^_\d+_' + re.escape(tool)
            function = list(filter((lambda x: re.search(r, x)), dir(module)))[0]
            if function:
                func = getattr(module, function)
                func()
