from typing import Dict

import click
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

# Exit codes
CONFIG_NOT_FOUND = 1
METADATA_NOT_FOUND = 2
STATE_CONFLICT = 3

@click.group()
def cli():
    pass

def __version_check(cfg_dict: Dict[str, str]):
    """
    Side-effect-ful version check: check config version and inform user as
    necessary.
    """
    version = cfg_dict.get("version")
    if version and version != VERSION:
        logging.warning("loading a chadow config from an old version.")
    elif not version:
        logging.warning("config does not specify a version.")

def __write_cfg(updated_config: Dict[str, str], config_filename: str, log_mesg: str):
    with open(config_filename, "w") as config_file:
        json.dump(updated_config, config_file)
    
    logging.info(log_mesg)

@cli.command()
@click.argument("name")
def createlib(name: str):
    def __createlib(cfg_file, comparator="filename"):
        config = json.load(cfg_file)
        __version_check(config)
        existing_libraries = config.get("libraryMapping", {})

        if name in existing_libraries:
            logging.error("specified name is already taken. Delete name first if you really want to use this name.")
            exit(STATE_CONFLICT)
        else:
            existing_libraries[name] = {
                "sectors": {},
                "comparator": comparator
            }

        config["libraryMapping"] = existing_libraries
        return config

    config_filename = os.path.join(APP_ROOT, CONFIG_NAME)
    updated_config = None
    try:
        with open(config_filename, "r") as config_file:
            updated_config = __createlib(config_file)
        __write_cfg(updated_config, config_filename, "Created new lib: %s" % name)
    except json.decoder.JSONDecodeError:
        # Config file is malformed json. Maybe a botched install. But let's be
        # forgiving anyway and reformat the malformed config.
        with open(config_filename, "w+") as config_file:
            logging.warning("unreadable json in config file. Reformatting.")
            config_file.write('{"version": "%s", "libraryMapping": {}}' % VERSION)
            config_file.flush()

        with open(config_filename, "r") as config_file:
            updated_config = __createlib(config_file)
        __write_cfg(updated_config, config_filename, "Created new lib: %s" % name)

@cli.command()
@click.argument("name")
def deletelib(name: str):
    try:
        config_filename = os.path.join(APP_ROOT, CONFIG_NAME)
        with open(config_filename) as config_file:
            config = json.load(config_file)
            __version_check(config)
            existing_libraries = config.get("libraryMapping", {})

            if name in existing_libraries:
                del existing_libraries[name]
                # FIXME is this still necessary?
                config["libraryMapping"] = existing_libraries
                __write_cfg(config, config_filename, "Deleted library: %s" % name)
            else:
                logging.error("asked to delete a nonexistent library.")
                exit(STATE_CONFLICT)
    except FileNotFoundError:
        logging.error("config file not found. Is chadow installed properly?")
        exit(CONFIG_NOT_FOUND)

@cli.command()
@click.argument("library")
@click.argument("sector_name")
@click.argument("sector_path")
def regsector(library: str, sector_name: str, sector_path: str):
    # TODO Make sure this is atomic.
    logging.info("asked to register sector %s" % sector_path)
    try:
        config = None
        config_filename = os.path.join(APP_ROOT, CONFIG_NAME)
        with open(os.path.join(APP_ROOT, CONFIG_NAME)) as config_file:
            config = json.load(config_file)
            __version_check(config)

            libsectors = config["libraryMapping"][library]["sectors"]
            if sector_name in libsectors:
                logging.error("sector %s already exists in library %s" % (sector_name, library))
                exit(STATE_CONFLICT)
            
        metadata_path = os.path.join(sector_path, CHADOW_METADATA)
        if os.path.isfile(metadata_path):
            logging.error("specified sector_path %s is already registered." % sector_path)
            exit(STATE_CONFLICT)

        try:
            with open(os.path.join(sector_path, CHADOW_METADATA), "w+") as metadata:
                metadata.write(sector_name)
                metadata.flush()
        except FileNotFoundError:
            logging.error("metadata can't be opened. Please check the sector path and/or the permissions to the path.")
            exit(METADATA_NOT_FOUND)
        
        config["libraryMapping"][library]["sectors"][sector_name] = sector_path
        __write_cfg(
            config, config_filename,
            "Created sector %s for library %s at %s." % (sector_name, library, sector_path)
        )
    except FileNotFoundError:
        logging.error("config file not found. Is chadow installed properly?")
        exit(CONFIG_NOT_FOUND)

if __name__ == "__main__":
    cli()
