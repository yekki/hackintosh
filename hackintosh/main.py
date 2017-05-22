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
@pass_context
def cli(ctx, verbose, local):
    ctx.verbose = verbose
    ctx.is_local_repo = local
    cleanup()


'''
@cli.command()
@click.option('-s', '--series', default='z30-b', required=True, type=click.Choice(['x220', 't440-p', 'z30-b']))
@pass_context
def acpi(ctx, series):
    ctx.series = series
    execute(ctx, inspect.getframeinfo(frame = inspect.currentframe()).function)

'''
'''
@cli.command()
@click.option('--type', type=click.Choice(['alc', 'voodoo','patcher']), default='alc')
def hda(type):
    if type == 'alc': download_alc()
    if type == 'voodoo': download_voodoo()

    unzip_dir('./stage', './output')


#@click.option('--series', prompt=click.style('Your laptop series:', fg='green'), default='z30-b',
 #             help='Your laptop series in abbreviation, for example: x220')
#@click.option('--series', series_prompt)
@cli.command()
@click.pass_obj
def acpi(config):
    series = click.(show_default='z30-b', text='Please input your laptop series')
    #print(series)
    #load_laptop_meta(config, series)
    print(series)


@cli.command()
@click.pass_obj
def acpi(config):
    initialize(config)
    prepare_acpi_files(config)
    decompile(config)
    apply_dsdt_patches(config)
    apply_ssdt_patches(config)
    compile_acpi(config)
    customize(config)
'''
