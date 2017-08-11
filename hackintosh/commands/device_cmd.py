from hackintosh import ALL_META, OUTPUT_DIR, REPO_ROOT
from hackintosh.lib import download_rehabman, cleanup, unzip, cleanup_dirs
from string import Template
import click, shutil, os

@click.group(short_help="Commands for external devices.")
def cli():
    pass


@cli.command(short_help='Prepare all stuff for device.')
@click.option('-i', '--id', required=True, type=click.Choice(ALL_META['external_device'].keys()),
              help='Choose the laptop series')
def build(id):
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
