from hackintosh import CLIENT_SETTINGS, ALL_META, STAGE_DIR, OUTPUT_DIR, PKG_ROOT, save_conf
from hackintosh.lib import message, cleanup, execute, zip_dir, to_num, download_project, unzip
from subprocess import call

import click, os, shutil


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
@click.option('-s', '--series', required=True, type=click.Choice(ALL_META['certified']['series']),
              help='Choose the laptop series')
def laptop(series):
    if series in ALL_META['supported']:
        CLIENT_SETTINGS['current_series'] = series
        save_conf(CLIENT_SETTINGS)
        message(f'Your current laptop series is {series}')


@cli.command(short_help='Open urls.')
def open():
    ans = True
    while ans:

        print('\n'.join([f"{i+1}.{v['desc']}" for i, v in enumerate(ALL_META['bookmark'])]) + "\n" + str(len(ALL_META['bookmark']) + 1) + '.Exit\n')

        ans = input("What would you like to access? ")

        index = to_num(ans)

        if index == 0:
            print("\n Not Valid Choice Try again")
        elif index == len(ALL_META['bookmark']) + 1:
            print("\n Goodbye")
            ans = None
        else:
            m = ALL_META['bookmark'][index-1]

            if m['uri'].startswith('http'):
                click.launch(m['uri'])
            else:
                call(["open " + m['desc']], shell=True)



@cli.command(short_help='Download Apps.')
@click.argument('kexts', nargs=-1, type=click.STRING)
def download(kexts):
    cleanup()
    for k in kexts:
        if k in ALL_META['projects'].keys():
            download_project(ALL_META['projects'][k])
        else:
            message(f'{k} is not supported.')
    unzip()
    pass