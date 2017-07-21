from hackintosh import *


@click.group()
def cli():
    pass


@cli.command(short_help='Switch Repo location: pkg or local.')
def switch_repo():
    loc = CONFIG['repo_location']
    if loc == 'pkg':
        CONFIG['repo_location'] = 'local'
        info('switch to local repo')
    elif loc == 'local':
        CONFIG['repo_location'] = 'pkg'
        info('switch to pkg repo')

    save_conf(CONFIG)


@cli.command(short_help='Set default laptop series.')
def laptop():
    while True:
        value = click.prompt('Please enter a valid laptop series', type=str)
        if value in CONFIG['supported_series']:
            CONFIG['current_series'] = value
            save_conf(CONFIG)
            info(f'Your current laptop series is {value}')
            break
