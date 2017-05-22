import click
from hackintosh.main import pass_context

@click.group()
@pass_context
def cli(ctx):
    print('hello')


@cli.command()
def say():
    print('world!')
