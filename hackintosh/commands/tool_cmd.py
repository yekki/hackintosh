from hackintosh import *
from hackintosh.commands import execute_module

@click.command()
@click.option('-a', '--all', is_flag=True, help='Update all tools & patches.')
@click.option('-t', '--tool', type=click.Choice(['iasl', 'pathmatic', 'patches', 'ssdtPRgen']),
              help='choose the tool which will be updated.')
def cli(all, tool):
    if all:
        execute_module('tool')
    else:
        if tool:
            module = importlib.import_module(f'hackintosh.commands.tool_impl')
            r = r'^_\d+_' + re.escape(tool)
            function = list(filter((lambda x: re.search(r, x)), dir(module)))[0]
            if function:
                func = getattr(module, function)
                func()
