import click
import os
import json

VERSION = "0.1.0"
APP_ROOT = "~/.chadow"
CONFIG_NAME = "config.json"

@click.group()
def cli():
    pass

def __version_check(cfg_dict):
    """
    Side-effect-ful version check.
    """
    version = cfg_dict.get("version")
    if version and version != VERSION
        print("WARNING: loading a chadow config from an old version.")
    elif not version:
        print("WARNING: config does not specify a version.")

@cli.command()
@click.argument("name")
def createlib(name):
    def __createlib(cfg_file):
        config = json.load(cfg_file)
        __version_check(cfg_dict)
        existing_libraries = config.get("libraries", {})

        if name in existing_libraries:
            print("ERROR: specified name is already taken. Delete name first if you really want to use this name.")
            exit(1)
        else:
            existing_libraries[name] = {
                "sectors": {}
            }

        config["libraries"] = existing_libraries

    try:
        with open(os.path.join(APP_ROOT, CONFIG_NAME)) as config_file:
            __createlib(config_lib)
    except FileNotFoundError:
        # Maybe a botched install. But let's be forgiving anyway.
        with open(os.path.join(APP_ROOT, CONFIG_NAME), "w+") as config_file:
            __createlib(config_file)

@cli.command()
@click.argument("name")
def deletelib(name):
    try:
        with open(os.path.join(APP_ROOT, CONFIG_NAME)) as config_file:
            config = json.load(cfg_file)
            __version_check(cfg_dict)
            existing_libraries = config.get("libraries", {})

            if name in existing_libraries:
                del existing_libraries[name]
            else:
                print("ERROR: asked to delete a nonexistent library.")
                exit(1)
    except FileNotFoundError:
        print("ERROR: config file not found. Is chadow installed properly?")
        exit(1)

if __name__ == "__main__":
    cli()
