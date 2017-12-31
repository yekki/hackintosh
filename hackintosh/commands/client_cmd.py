from hackintosh import CLIENT_SETTINGS, ALL_META, STAGE_DIR, OUTPUT_DIR, LAPTOP_META, PKG_ROOT, CLIENT_SETTINGS_FILE, save_conf, error
from hackintosh.lib import cleanup, execute, zip_dir, to_num, download_project, unzip, download_kexts, print_project, cleanup_dirs, clover_kext_patches
from subprocess import check_call, CalledProcessError

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
    click.echo('This is a time-consuming operation...')
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
            click.echo('Switched to local repository.')
        elif loc == 'local':
            CLIENT_SETTINGS['repo_location'] = 'pkg'
            click.echo('Switched to pkg repository.')
        else:
            raise ValueError(f'Unsupported repository type: {loc}')

    save_conf(CLIENT_SETTINGS)


@cli.command(short_help='Clone local Repository.')
def clone_repo():
    shutil.copytree(os.path.join(PKG_ROOT, 'repo'),
                    os.path.join(os.getcwd(), 'repo'))
    click.echo('Created local repository stub directory.')


@cli.command(short_help='Show current client settings.')
def info():
    click.secho('Hackintosh Workbench Version: ', bold=True)
    click.secho(CLIENT_SETTINGS['version'], fg='green')
    click.secho('Laptop Series: ', bold=True)
    click.secho(CLIENT_SETTINGS['current_series'], fg='green')
    click.secho('Repository Location: ', bold=True)
    click.secho(CLIENT_SETTINGS['repo_location'], fg='green')


@cli.command(short_help='Set default laptop series.')
@click.option('-s', '--series', required=True, type=click.Choice(ALL_META['certified']['series']),
              help='Choose the laptop series')
def laptop(series):
    if series in ALL_META['supported']:
        CLIENT_SETTINGS['current_series'] = series
        save_conf(CLIENT_SETTINGS)
        click.echo(f'Your current laptop series is {series}')


@cli.command(short_help='Open urls.')
def open():
    ans = True
    while ans:

        click.echo('\n'.join([f"{i+1}.{v['desc']}" for i, v in enumerate(ALL_META['bookmark'])]) + "\n" + str(len(ALL_META['bookmark']) + 1) + '.Exit\n')

        click.echo("What would you like to access? ")
        ans = click.getchar()

        index = to_num(ans)

        if index == 0:
            click.secho("\n Not Valid Choice Try again", fg="red")
        elif index == len(ALL_META['bookmark']) + 1:
            click.echo("\n Goodbye")
            ans = None
        else:
            m = ALL_META['bookmark'][index-1]

            if m['uri'].startswith('http'):
                click.launch(m['uri'])
            else:
                #call(["open " + m['desc']], shell=True)
                click.launch(m['uri'], locate=True)
        click.clear()

@cli.command(short_help='Install widgets.')
@click.option('-v', '--voodoops2', is_flag=True,
              help='Install VoodooPS2Daemon & org.rehabman.voodoo.driver.Daemon.plist')
def install(voodoops2):
    if voodoops2:
        if not os.path.exists(os.path.join(OUTPUT_DIR, 'VoodooPS2Daemon')) or os.path.exists(
                os.path.join(OUTPUT_DIR, 'org.rehabman.voodoo.driver.Daemon.plist')):
            click.echo("VoodooPS2 isn't exists, downloading it now...")
            download_project(ALL_META['kext']['supported']['os-x-voodoo-ps2-controller'])
            unzip(ALL_META['kext']['essential']['os-x-voodoo-ps2-controller'])

            click.echo("VoodooPS2 downloaded, installing now...")

        try:
            check_call(f'sudo cp {OUTPUT_DIR}/VoodooPS2Daemon /usr/bin', shell=True)
            click.echo('VoodooPS2Daemon is installed.')
        except CalledProcessError:
            error('Failed to install VoodooPS2 widgets: VoodooPS2Daemon')

        try:
            check_call(f'sudo cp {OUTPUT_DIR}/org.rehabman.voodoo.driver.Daemon.plist /Library/LaunchDaemons',
                       shell=True)
            click.echo('org.rehabman.voodoo.driver.Daemon.plist is installed.')
        except CalledProcessError:
            error('Failed to install VoodooPS2 widgets: org.rehabman.voodoo.driver.Daemon.plist')


@cli.command(short_help='Download projects.')
@click.argument('projects', nargs=-1, type=click.STRING)
def download(kexts):
    cleanup()
    for k in kexts:
        if k in ALL_META['projects'].keys():
            download_project(ALL_META['projects'][k])
        else:
            click.echo(f'{k} is not supported.')
    unzip()
    pass


@cli.command(short_help=f"Download kexts for laptop:{CLIENT_SETTINGS['current_series']}")
def laptop():
    cleanup()

    click.echo(f"Downloading kexts for laptop:{CLIENT_SETTINGS['current_series']}:")

    kexts = []

    k1 = download_kexts(ALL_META['patches']['system']['kexts'])
    k2 = download_kexts(LAPTOP_META['kexts'])

    kexts.extend(k1)
    kexts.extend(k2)

    if kexts is not None:
        unzip(kexts)


@cli.command(short_help='Show all app projects.')
def app_info():
    click.secho('Supported app projects:', bold=True)
    [print_project(v) for v in ALL_META['projects'].values() if v['type'] == 'app']

    click.secho('Supported pkg projects:', bold=True)
    [print_project(v) for v in ALL_META['projects'].values() if v['type'] == 'pkg']


@cli.command(short_help='Show all kext projects.')
@click.option('-s', '--supported', is_flag=True, help='Show all supported kext projects.')
@click.option('-l', '--laptop', is_flag=True, help='Show kexts for current laptop.')
@click.option('-c', '--common', is_flag=True, help='Show system kexts for hackintosh installation.')
def kext_info(supported, laptop, common):

    if supported:
        click.echo('Supported kexts projects:')
        [print_project(v) for v in ALL_META['projects'].values() if v['type'] == 'kext']


    if laptop:
        click.echo(f"kexts for laptop {CLIENT_SETTINGS['current_series']}:")
        projects = {}
        projects.update(LAPTOP_META['kexts'])
        projects.update(ALL_META['patches']['system']['kexts'])
        for k, v in projects.items():
            pmeta = ALL_META['projects'][k]
            kexts = ','.join(v)
            print_project(pmeta, kexts)

    if common:
        click.echo('kexts for all laptops:')
        for k, v in ALL_META['patches']['system']['kexts'].items():
            pmeta = ALL_META['projects'][k]
            kexts = ','.join(v)
            print_project(pmeta, kexts)


@cli.command(short_help="Commands for external devices.")
@click.option('-i', '--id', required=True, type=click.Choice(ALL_META['external_device'].keys()),
              help='Choose the device id')
def device(id):
    cleanup()
    download_kexts(ALL_META['external_device'][id]['kexts'])
    unzip()

    cleanup_dirs(os.path.join(OUTPUT_DIR, 'kexts'), os.path.join(OUTPUT_DIR, 'clover'))

    for k in os.listdir(OUTPUT_DIR):
        if k.endswith('.kext'):
            shutil.move(os.path.join(OUTPUT_DIR, k), os.path.join(OUTPUT_DIR, 'kexts'))

    clover_kext_patches(ALL_META['external_device'][id]['clover']['kexts_to_patch'],
                        os.path.join(OUTPUT_DIR, 'clover', 'patch.plist'))


@cli.command(short_help="Edit client config file.")
def edit():
    click.edit(filename=CLIENT_SETTINGS_FILE)