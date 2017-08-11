import click


@click.command(short_help='Open helpful urls.')
@click.option('-r', '--rehabman', is_flag=True, help='Access Rehabman\'s github')
@click.option('-y', '--yekki', is_flag=True, help='Access yekki\'s github')
@click.option('-t', '--tonymacx86', is_flag=True, help='Access tonymacx86 website')
def cli(rehabman, yekki, tonymacx86):
    if tonymacx86: click.launch('https://www.tonymacx86.com/forums/sierra-laptop-support.188/')
    if yekki: click.launch('https://github.com/yekki')
    if rehabman: click.launch('https://github.com/rehabman')
