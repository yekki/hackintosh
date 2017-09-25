from hackintosh import CLIENT_SETTINGS, ALL_META, save_conf, error, message

import click, logging


@click.group(short_help='Commands for setting client settings.')
def cli():
    pass


@cli.command(short_help='Switch Repository location: pkg or local.')
def switch():
    loc = CLIENT_SETTINGS['repo_location']
    if loc == 'pkg':
        CLIENT_SETTINGS['repo_location'] = 'local'
        logging.info('switch to local repo')
    elif loc == 'local':
        CLIENT_SETTINGS['repo_location'] = 'pkg'
        logging.info('switch to pkg repo')

    save_conf(CLIENT_SETTINGS)


@cli.command(short_help='Show current client settings.')
def info():
    message({'Hackintosh Workbench Version: ': 'blue', click.style(CLIENT_SETTINGS['version']): 'green'})
    message({'Laptop Series: ': 'blue', click.style(CLIENT_SETTINGS['current_series']): 'green'})
    message({'Repository Location: ': 'blue', click.style(CLIENT_SETTINGS['repo_location']): 'green'})


@cli.command(short_help='Set default laptop series.')
@click.option('-s', '--series', required=True, type=click.Choice(ALL_META['supported']),
              help='Choose the laptop series')
def laptop(series):
    if series in ALL_META['supported']:
        CLIENT_SETTINGS['current_series'] = series
        save_conf(CLIENT_SETTINGS)
        message(f'Your current laptop series is {series}')
