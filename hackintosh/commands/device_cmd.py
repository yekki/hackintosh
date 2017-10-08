from hackintosh import ALL_META, OUTPUT_DIR
from hackintosh.lib import cleanup, unzip, cleanup_dirs, clover_kext_patches, message, download_kext
import click, shutil, os


@click.command(short_help="Commands for external devices.")
@click.option('-i', '--id', required=True, type=click.Choice(ALL_META['external_device'].keys()),
              help='Choose the device id')
def cli(id):
    cleanup()
    kexts = []
    for k, v in ALL_META['external_device'][id]['kext'].items():
        download_kext(ALL_META['kext']['supported'][k])
        kexts.extend(v)

    unzip(kexts)

    cleanup_dirs(os.path.join(OUTPUT_DIR, 'kexts'), os.path.join(OUTPUT_DIR, 'clover'))

    for k in os.listdir(OUTPUT_DIR):
        if k.endswith('.kext'):
            shutil.move(os.path.join(OUTPUT_DIR, k), os.path.join(OUTPUT_DIR, 'kexts'))

    clover_kext_patches(ALL_META['external_device'][id]['clover']['kexts_to_patch'],
                        os.path.join(OUTPUT_DIR, 'clover', 'patch.plist'))

    message(f'Finished.')
