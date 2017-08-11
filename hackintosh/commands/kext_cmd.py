from hackintosh import ALL_META, LAPTOP_META, OUTPUT_DIR, REPO_ROOT
from hackintosh.lib import download_rehabman, cleanup, unzip, delete, cleanup_dirs, rebuild_kextcache
from string import Template
from subprocess import call
import click, os, shutil, glob


@click.group(help='Commands for download hackintosh kexts.')
def cli():
    pass


@cli.command(short_help='Download kexts.')
@click.argument('kexts', nargs=-1, type=click.STRING)
def download(kexts):
    cleanup()

    for k in kexts:
        if k in ALL_META['kext']['supported']:
            download_rehabman(k)

    unzip()


@cli.command(short_help='Download kexts for laptop')
def laptop():
    #cleanup()

    projects = ALL_META['kext']['essential']['projects'] + LAPTOP_META['kext']['projects']
    kexts = ALL_META['kext']['essential']['widgets'] + LAPTOP_META['kext']['widgets']
    #for p in projects:
    #    download_rehabman(p)

    unzip()

    for k in os.listdir(OUTPUT_DIR):
        if k in kexts:
            continue
        else:
            path = os.path.join(OUTPUT_DIR, k)

            delete(path)


@cli.command(short_help='Install kexts to L/E')
def install():
    path = os.path.join(OUTPUT_DIR, 'kexts')
    if not os.path.exists(path):
        path = OUTPUT_DIR

    for k in os.listdir(path):
        call(['sudo', 'cp', '-r', os.path.join(path, k), '/Library/Extensions/'])
    else:
        pass
        rebuild_kextcache()



@cli.command(short_help='Prepare all stuff for device.')
@click.option('-i', '--id', required=True, type=click.Choice(ALL_META['external_device'].keys()),
              help='Choose the laptop series')
def device(id):
    cleanup()
    click.echo(click.style('downloading kexts...', fg='blue'))

    for p in ALL_META['external_device'][id]['kext']['projects']:
        download_rehabman(p)

    unzip(ALL_META['external_device'][id]['kext']['widgets'])

    cleanup_dirs(os.path.join(OUTPUT_DIR, 'kexts'), os.path.join(OUTPUT_DIR, 'clover'))

    for k in os.listdir(OUTPUT_DIR):
        if k.endswith('.kext'):
            shutil.move(os.path.join(OUTPUT_DIR, k), os.path.join(OUTPUT_DIR, 'kexts'))

    click.echo(click.style('creating clover patches...', fg='blue'))

    templ = Template(open(os.path.join(REPO_ROOT, 'config', 'clover_kexts_to_patch.templ')).read())

    with open(os.path.join(OUTPUT_DIR, 'clover', 'patch.plist'), 'a') as f:
        for p in ALL_META['external_device'][id]['clover']['kexts_to_patch']:
            content = templ.substitute(p)
            f.write(content)


@cli.command(short_help='Show all supported kexts.')
@click.option('-s', '--supported', is_flag=True, help='Show all supported kexts.')
@click.option('-l', '--laptop', is_flag=True, help='Show kexts for laptop.')
@click.option('-e', '--essential', is_flag=True, help='Show essential kexts for hackintosh installation.')
def info(supported, laptop, essential):
    if supported:
        for k in ALL_META['kext']['supported']:
            print(k)

    if laptop:
        for k in LAPTOP_META['kexts']:
            print(k)

    if essential:
        for k in ALL_META['kext']['essential']:
            print(k)
