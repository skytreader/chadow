import click
import os
import json

VERSION = "0.1.0"
APP_ROOT = "~/.chadow"
CONFIG_NAME = "config.json"

@click.group()
def cli():
    pass

@cli.command()
@click.argument("name")
def createlib(name):
    def __createlib(cfg_file):
        config = json.load(cfg_file)

        version = config.get("version")
        if version and version != VERSION:
            print("WARNING: loading a chadow config from an old version.")
        elif not version:
            print("WARNING: config does not specify a version.")

        existing_libraries = config.get("libraries", {})

        if name in existing_libraries:
            print("ERROR: specified name is already taken. Delete name first if you really want to use this name.")
        else:
            existing_libraries[name] = {
                "sectors": {}
            }

        config["libraries"] = existing_libraries

    try:
        with open(os.path.join(APP_ROOT, CONFIG_NAME)) as config_file:
            __createlib(config_lib)
    except FileNotFoundError:
        # Fresh chadow install
        with open(os.path.join(APP_ROOT, CONFIG_NAME), "w+") as config_file:
            __createlib(config_file)

if __name__ == "__main__":
    cli()
