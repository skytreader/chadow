import click

@click.group()
def spam():
    pass

@click.command()
@click.argument("name")
def createlib(name):
    print("Creating data library %s..." % name)

spam.add_command(createlib)
