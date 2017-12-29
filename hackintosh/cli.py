from hackintosh import PKG_ROOT, error, debug
from hackintosh.lib import cleanup

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
        ns = {}
        fn = f"{os.path.join(PKG_ROOT, 'commands')}/{name}_cmd.py"

        if os.path.exists(fn):
            with open(fn) as f:
                code = compile(f.read(), fn, 'exec')
                eval(code, ns, ns)
        elif name == 'cleanup':
            cleanup()
            click.clear()
            return
        else:
            return

        return ns['cli']