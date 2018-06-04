import click
import io
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_version():
    # The VERSION file should have only one line ever.
    with open("VERSION") as v:
        for line in v:
            return line.strip()

VERSION = get_version()
APP_ROOT = os.path.expanduser("~/.chadow")
CONFIG_NAME = "config.json"
CHADOW_METADATA = ".chadow-metadata"

@click.group()
def cli():
    pass

def __version_check(cfg_dict):
    """
    Side-effect-ful version check.
    """
    version = cfg_dict.get("version")
    if version and version != VERSION:
        logging.warning("loading a chadow config from an old version.")
    elif not version:
        logging.warning("config does not specify a version.")

@cli.command()
@click.argument("name")
def createlib(name):
    def __createlib(cfg_file):
        config = json.load(cfg_file)
        __version_check(config)
        existing_libraries = config.get("libraries", {})

        if name in existing_libraries:
            logging.error("specified name is already taken. Delete name first if you really want to use this name.")
            exit(1)
        else:
            existing_libraries[name] = {
                "sectors": {}
            }

        config["libraries"] = existing_libraries
        return config

    def __writelib(updated_config, config_filename):
        with open(config_filename, "w") as config_file:
            json.dump(updated_config, config_file)
        
        logging.info("Created new lib: %s" % name)

    config_filename = os.path.join(APP_ROOT, CONFIG_NAME)
    updated_config = None
    try:
        with open(config_filename, "r") as config_file:
            updated_config = __createlib(config_file)
        __writelib(updated_config, config_filename)
    except io.UnsupportedOperation:
        # Config file is malormed json. Maybe a botched install. But let's be
        # forgiving anyway and reformat the malformed config.
        with open(config_filename, "w+") as config_file:
            logging.warning("unreadable json in config file. Reformatting.")
            config_file.write('{"version": "%s"}' % VERSION)
            config_file.flush()
            updated_config = __createlib(config_file)
        __writelib(updated_config, config_filename)

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
                logging.error("asked to delete a nonexistent library.")
                exit(1)
    except FileNotFoundError:
        logging.error("config file not found. Is chadow installed properly?")
        exit(1)

@cli.command()
@click.argument("library")
@click.argument("sector_name")
@click.argument("sector_path")
def regsector(library, sector_name, sector_path):
    pass

if __name__ == "__main__":
    cli()
