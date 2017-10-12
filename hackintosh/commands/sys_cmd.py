from hackintosh import CLIENT_SETTINGS, ALL_META, PKG_ROOT, save_conf
from hackintosh.lib import message
from subprocess import call, Popen, PIPE

import click, os, shutil


@click.group(short_help='Commands for setting client settings.')
def cli():
    pass


@cli.command(short_help='Archive problem reporting files.')
def problem_reports():
    k = Popen(['kextstat'], stdout=PIPE)
    k2 = Popen(['grep', '-y', 'acpiplat'], stdin=k.stdout, stdout=PIPE)
    out1 = k2.communicate()
    print(out1)

    k3 = Popen(['grep', '-y', 'appleintelcpu'], stdin=k.stdout, stdout=PIPE)
    out2 = k3.communicate()
    print(out2)

    k4 = Popen(['grep', '-y', 'applelpc'], stdin=k.stdout, stdout=PIPE)
    out3 = k4.communicate()
    print(out3)

    k5 = Popen(['grep', '-y', 'applehda'], stdin=k.stdout, stdout=PIPE)
    out4 = k5.communicate()
    print(out4)

    out5 = call('ls -l /System/Library/Extensions/AppleHDA.kext/Contents/Resources/*.zml*', shell=True)
    print(out5)

    out6 = call('pmset -g assertions', shell=True)
    print(out6)

    k = Popen(['system_profiler', 'SPSerialATADataType'], stdout=PIPE)
    k6 = Popen(['grep', 'TRIM'], stdin=k.stdout, stdout=PIPE)
    out7 = k6.communicate()
    print(out7)

    out8 = call('sudo touch /System/Library/Extensions', shell=True)
    print(out8)

    out9 = call('sudo kextcache -u', shell=True)
    print(out9)


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
    shutil.copytree(os.path.join(PKG_ROOT, 'repo'), os.path.join(os.getcwd(), 'repo'))
    message('Created local repository stub directory.')


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
