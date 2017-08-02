from hackintosh import PKG_ROOT
from pathlib import Path
import click, os, logging, glob


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
            logging.critical(e)
            exit(-1)
        else:
            return mod.cli
