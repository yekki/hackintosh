import click


@click.command()
def cli():
    MARKER = '# Everything below is ignored\n'
    message = click.edit('\n\n' + MARKER)
    print(message)
    if message is not None:
        return message.split(MARKER, 1)[0].rstrip('\n')

