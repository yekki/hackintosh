from hackintosh.main import pass_context
from hackintosh.app import update_patches, update_iasl, update_patchmatic, update_ssdt
from hackintosh.utils import cprint

import click


@click.group()
@pass_context
def cli(ctx):
    pass

@cli.command()
def update():
    click.clear()
    menu = 'Main'
    while 1:
        if menu == 'Main':
            cprint('########################')
            cprint('#     Main Menu        #')
            cprint('#  i: iasl             #')
            cprint('#  p: patchmatic       #')
            cprint('#  s: ssdtPRGen        #')
            cprint('#  u: dsdt & ssdt(s)   #')
            cprint('#  q: quit             #')
            cprint('########################')

            char = click.getchar()
            click.clear()

            if char == 'i':
                update_iasl()
                print('iasl is updated.')
            elif char == 'p':
                update_patchmatic()
                print('patchmatic is updated.')
            elif char == 's':
                update_ssdt()
                print('ssdtPRGen is updated.')
            elif char == 'u':
                update_patches()
                print('dsdt & dsdt(s) patches are updated.')
            elif char == 'q':
                menu = 'Quit'
            else:
                click.echo('Invalid input.')

        elif menu == 'Quit':
            return
