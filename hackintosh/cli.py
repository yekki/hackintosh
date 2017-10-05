from hackintosh import PKG_ROOT
from hackintosh.lib import error
from pathlib import Path
import click, os, glob


class MainCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        files = glob.glob(f"{os.path.join(PKG_ROOT, 'commands')}/*_cmd.py")

        for fn in files:
            rv.append(Path(fn).stem.replace('_cmd', ''))
            rv.sort()

        return rv

    def get_command(self, ctx, name):
        try:
            if name.endswith('.py'):
                return
            mod = __import__(f'hackintosh.commands.{name}_cmd', None, None, ['cli'])
        except ImportError as e:
            error(f"Failed to load command:{name}, error:{e}")
        else:
            return mod.cli
