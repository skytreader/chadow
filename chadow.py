import click

@click.group()
def cli():
    pass

@cli.command()
def createlib():
    # print("Creating data library %s..." % name)
    print("Hello world.")

if __name__ == "__main__":
    cli()
