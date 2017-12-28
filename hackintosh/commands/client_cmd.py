from hackintosh import CLIENT_SETTINGS, ALL_META, STAGE_DIR, OUTPUT_DIR, PKG_ROOT, REPO_ROOT, save_conf
from hackintosh.lib import message, cleanup, execute, zip_dir, del_by_exts, cleanup_dir
from subprocess import call

import click, os, shutil, glob


@click.group(short_help='Commands for system maintenances.')
def cli():
    pass


@cli.command(short_help='Archive problem reporting files.')
def reports():
    cleanup()

    execute('kextstat | grep -y acpiplat', 'acpiplat.out')
    execute('kextstat | grep -y applelpc', 'applelpc.out')
    execute('kextstat | grep -y appleintelcpu', 'appleintelcpu.out')
    execute('kextstat | grep -y applehda', 'applehda.out')
    execute('ls -l /System/Library/Extensions/AppleHDA.kext/Contents/Resources/*.zml*',
            'applehda_res.out')
    execute('pmset -g assertions', 'assertions.out')
    execute('system_profiler SPSerialATADataType | grep TRIM', 'assertions.out')
    message('This is a time-consuming operation...')
    execute(
        'sudo touch /System/Library/Extensions && sudo kextcache -u /', 'kextcache.out')

    # TODO: fix the structure in zip file
    zip_dir(STAGE_DIR, os.path.join(OUTPUT_DIR, 'out.zip'), '.out')


@cli.command(short_help='Switch repository location: pkg or local.')
def switch_repo():
    if CLIENT_SETTINGS['repo_fixed']:
        CLIENT_SETTINGS['repo_fixed'] = False
    else:
        loc = CLIENT_SETTINGS['repo_location']
        if loc == 'pkg':
            CLIENT_SETTINGS['repo_location'] = 'local'
            message('Switched to local repository.')
        elif loc == 'local':
            CLIENT_SETTINGS['repo_location'] = 'pkg'
            message('Switched to pkg repository.')
        else:
            raise ValueError(f'Unsupported repository type: {loc}')

    save_conf(CLIENT_SETTINGS)


@cli.command(short_help='Clone local Repository.')
def clone_repo():
    shutil.copytree(os.path.join(PKG_ROOT, 'repo'),
                    os.path.join(os.getcwd(), 'repo'))
    message('Created local repository stub directory.')


@cli.command(short_help='Show current client settings.')
def info():
    message({'Hackintosh Workbench Version: ': 'blue',
             click.style(CLIENT_SETTINGS['version']): 'green'})
    message({'Laptop Series: ': 'blue', click.style(
        CLIENT_SETTINGS['current_series']): 'green'})
    message({'Repository Location: ': 'blue', click.style(
        CLIENT_SETTINGS['repo_location']): 'green'})


@cli.command(short_help='Set default laptop series.')
@click.option('-s', '--series', required=True, type=click.Choice(ALL_META['supported']),
              help='Choose the laptop series')
def laptop(series):
    if series in ALL_META['supported']:
        CLIENT_SETTINGS['current_series'] = series
        save_conf(CLIENT_SETTINGS)
        message(f'Your current laptop series is {series}')
