from hackintosh import CLIENT_SETTINGS, ALL_META, save_conf

import click, logging, pprint


@click.group(short_help='Commands for setting client settings.')
def cli():
    pass


@cli.command(short_help='Switch Repo location: pkg or local.')
def switch_repo():
    loc = CLIENT_SETTINGS['repo_location']
    if loc == 'pkg':
        CLIENT_SETTINGS['repo_location'] = 'local'
        logging.info('switch to local repo')
    elif loc == 'local':
        CLIENT_SETTINGS['repo_location'] = 'pkg'
        logging.info('switch to pkg repo')

    save_conf(CLIENT_SETTINGS)


@cli.command(short_help='Switch Repo location: pkg or local.')
def info():
    pprint.pprint(CLIENT_SETTINGS)


@cli.command(short_help='Set default laptop series.')
@click.option('-s', '--series', required=True, type=click.Choice(ALL_META['supported']),
              help='Choose the laptop series')
def laptop(series):
    if series in ALL_META['supported']:
        CLIENT_SETTINGS['current_series'] = series
        save_conf(CLIENT_SETTINGS)
        logging.info(f'Your current laptop series is {series}')
