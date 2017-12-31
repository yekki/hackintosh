import click

APP_NAME = 'yekki'

@click.command()
def cli():
    print(click.get_app_dir(APP_NAME))

