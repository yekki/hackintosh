import click

from hackintosh.utils import cleanup, Context, Path

import hackintosh.logger as logger
import inspect, os, sys

class HackintoshCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []

        for fn in os.listdir(os.path.join(Path.PKG_ROOT, 'commands')):
            rv.append(fn)

        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__(f'hackintosh.commands.cmd_{name}', None, None, ['cli'])
        except ImportError as e:
            logger.critical(e)

        return mod.cli


CONTEXT_SETTINGS = dict(auto_envvar_prefix='yekki')
pass_context = click.make_pass_decorator(Context, ensure=True)

@click.command(cls=HackintoshCLI, context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode.')
@click.option('-l', '--local', is_flag=True,
              help='Use the repository located at current directory.')
@click.option('-r', '--record', is_flag=True,
              help='Record all commands to recorder.log.')
@pass_context
def cli(ctx, verbose, local, record):
    ctx.verbose = verbose
    ctx.is_local_repo = local
    logger.RECORDER = record
    cleanup()
