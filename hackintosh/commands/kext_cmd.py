from hackintosh import ALL_META, LAPTOP_META, OUTPUT_DIR, CLIENT_SETTINGS, error
from hackintosh.lib import download_project, cleanup, unzip, message, print_kext, download_kexts
from subprocess import check_call, CalledProcessError
import click, os


@click.group(help='Commands for download hackintosh kexts.')
def cli():
    pass


@cli.command(short_help='Download kexts.')
@click.argument('kexts', nargs=-1, type=click.STRING)
def download(kexts):
    cleanup()

    for k in kexts:
        if k in ALL_META['kext']['supported'].keys():
            download_project(ALL_META['kext']['supported'][k])
        else:
            message(f'{k} is not supported.')
    unzip()


@cli.command(short_help='Install widgets.')
@click.option('-v', '--voodoops2', is_flag=True,
              help='Install VoodooPS2Daemon & org.rehabman.voodoo.driver.Daemon.plist')
def install(voodoops2):
    if voodoops2:
        if not os.path.exists(os.path.join(OUTPUT_DIR, 'VoodooPS2Daemon')) or os.path.exists(
                os.path.join(OUTPUT_DIR, 'org.rehabman.voodoo.driver.Daemon.plist')):
            message("VoodooPS2 isn't exists, downloading it now...")
            download_project(ALL_META['kext']['supported']['os-x-voodoo-ps2-controller'])
            unzip(ALL_META['kext']['essential']['os-x-voodoo-ps2-controller'])

        message("VoodooPS2 downloaded, installing now...")

        try:
            check_call(f'sudo cp {OUTPUT_DIR}/VoodooPS2Daemon /usr/bin', shell=True)
            message('VoodooPS2Daemon is installed.')
        except CalledProcessError:
            error('Failed to install VoodooPS2 widgets: VoodooPS2Daemon')

        try:
            check_call(f'sudo cp {OUTPUT_DIR}/org.rehabman.voodoo.driver.Daemon.plist /Library/LaunchDaemons',
                       shell=True)
            message('org.rehabman.voodoo.driver.Daemon.plist is installed.')
        except CalledProcessError:
            error('Failed to install VoodooPS2 widgets: org.rehabman.voodoo.driver.Daemon.plist')


@cli.command(short_help=f"Download kexts for laptop:{CLIENT_SETTINGS['current_series']}")
def laptop():
    cleanup()

    message(f"Downloading kexts for laptop:{CLIENT_SETTINGS['current_series']}:")

    kexts = []

    k1 = download_kexts(ALL_META['patches']['system']['kexts'])
    k2 = download_kexts(LAPTOP_META['kexts'])

    kexts.extend(k1)
    kexts.extend(k2)

    if kexts is not None:
        unzip(kexts)

@cli.command(short_help='Show all supported kexts.')
@click.option('-s', '--supported', is_flag=True, help='Show all supported kext projects.')
@click.option('-l', '--laptop', is_flag=True, help='Show kexts for current laptop.')
@click.option('-e', '--essential', is_flag=True, help='Show essential kexts for hackintosh installation.')
def info(supported, laptop, essential):
    if supported:
        message('Supported kext projects:')
        for k, v in ALL_META['kext']['supported'].items():
            pmeta = ALL_META['kext']['supported'][k]
            print_kext(pmeta)

    if laptop:
        message(f"kexts for laptop {CLIENT_SETTINGS['current_series']}:")
        projects = {}
        projects.update(LAPTOP_META['kext'])
        projects.update(ALL_META['kext']['essential'])
        for k, v in projects.items():
            pmeta = ALL_META['kext']['supported'][k]
            kexts = ','.join(v)
            print_kext(pmeta, kexts)

    if essential:
        message('kexts for all laptops:')
        for k, v in ALL_META['kext']['essential'].items():
            pmeta = ALL_META['kext']['supported'][k]
            kexts = ','.join(v)
            print_kext(pmeta, kexts)
