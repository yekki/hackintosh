import click
from subprocess import call


@click.command(short_help='Open helpful urls.')
@click.option('-l', '--le', is_flag=True, help='Open /Library/Extensions')
@click.option('-s', '--sle', is_flag=True, help='Open /System/Library/Extensions')
@click.option('-h', '--home', is_flag=True, help='Access yekki\'s home page')
@click.option('-r', '--rehabman', is_flag=True, help='Access Rehabman\'s github')
@click.option('-y', '--yekki', is_flag=True, help='Access yekki\'s github')
@click.option('-t', '--tonymacx86', is_flag=True, help='Access tonymacx86 website')
def cli(le, sle, home, rehabman, yekki, tonymacx86):
    if tonymacx86:
        click.launch(
            'https://www.tonymacx86.com/forums/sierra-laptop-support.188/')
    if home:
        click.launch('http://www.yekki.me')
    if yekki:
        click.launch('https://github.com/yekki')
    if rehabman:
        click.launch('https://github.com/rehabman')
    if le:
        call(['open /Library/Extensions'], shell=True)
    if sle:
        call(['open /System/Library/Extensions'], shell=True)
