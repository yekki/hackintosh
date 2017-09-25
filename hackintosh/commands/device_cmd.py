from hackintosh import ALL_META, OUTPUT_DIR
from hackintosh.lib import download_rehabman, cleanup, unzip, cleanup_dirs, clover_kext_patches, message
import click, shutil, os


@click.group(short_help="Commands for external devices.")
def cli():
    pass


@cli.command(short_help='Prepare all stuff for device.')
@click.option('-i', '--id', required=True, type=click.Choice(ALL_META['external_device'].keys()),
              help='Choose the laptop series')
def build(id):
    cleanup()

    for p in ALL_META['external_device'][id]['kext']['projects']:
        download_rehabman(p)

    unzip(ALL_META['external_device'][id]['kext']['widgets'])

    cleanup_dirs(os.path.join(OUTPUT_DIR, 'kexts'), os.path.join(OUTPUT_DIR, 'clover'))

    for k in os.listdir(OUTPUT_DIR):
        if k.endswith('.kext'):
            shutil.move(os.path.join(OUTPUT_DIR, k), os.path.join(OUTPUT_DIR, 'kexts'))

    clover_kext_patches(ALL_META['external_device'][id]['clover']['kexts_to_patch'],
                        os.path.join(OUTPUT_DIR, 'clover', 'patch.plist'))

    message(f'Finished.')
