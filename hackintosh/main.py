from hackintosh import *


@click.command(cls=MainCLI, context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', is_flag=True, help='Enables verbose mode.')
@click.option('-l', '--local', is_flag=True,
              help='Use the repository located at current directory.')
@click.option('-r', '--record', is_flag=True,
              help='Record all commands to recorder.log.')
@pass_context
def cli(ctx, verbose, local, record):
    pass
