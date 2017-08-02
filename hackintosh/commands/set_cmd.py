from hackintosh import CLIENT_SETTINGS, ALL_META, save_conf

import click, logging


@click.group()
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


@cli.command(short_help='Set default laptop series.')
def laptop():
    while True:
        value = click.prompt('Please enter a valid laptop series', type=str)
        if value in ALL_META['supported']:
            CLIENT_SETTINGS['current_series'] = value
            save_conf(CLIENT_SETTINGS)
            logging.info(f'Your current laptop series is {value}')
            break
