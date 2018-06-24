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

@click.group()
def cli():
    pass

def __version_check(cfg_dict):
    """
    Side-effect-ful version check: check config version and inform user as
    necessary.
    """
    version = cfg_dict.get("version")
    if version and version != VERSION:
        logging.warning("loading a chadow config from an old version.")
    elif not version:
        logging.warning("config does not specify a version.")

def __write_cfg(updated_config, config_filename, log_mesg):
    with open(config_filename, "w") as config_file:
        json.dump(updated_config, config_file)
    
    logging.info(log_mesg)

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
            config_file.write('{"version": "%s", "libraries": {}}' % VERSION)
            config_file.flush()

        with open(config_filename, "r") as config_file:
            updated_config = __createlib(config_file)
        __write_cfg(updated_config, config_filename, "Created new lib: %s" % name)

@cli.command()
@click.argument("name")
def deletelib(name):
    try:
        config_filename = os.path.join(APP_ROOT, CONFIG_NAME)
        with open(config_filename) as config_file:
            config = json.load(config_file)
            __version_check(config)
            existing_libraries = config.get("libraries", {})

            if name in existing_libraries:
                del existing_libraries[name]
                # FIXME is this still necessary?
                config["libraries"] = existing_libraries
                __write_cfg(config, config_filename, "Deleted library: %s" % name)
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
    # TODO Make sure this is atomic.
    try:
        config = None
        config_filename = os.path.join(APP_ROOT, CONFIG_NAME)
        with open(os.path.join(APP_ROOT, CONFIG_NAME)) as config_file:
            config = json.load(config_file)
            logging.info("Found config")
            __version_check(config)

            libsectors = config["libraries"][library]["sectors"]
            if sector_name in libsectors:
                logging.error("sector %s already exists in library %s" % (sector_name, library))
                exit(1)
            
        metadata_path = os.path.join(sector_path, CHADOW_METADATA)
        if os.path.isfile(metadata_path):
            logging.error("specified sector_path %s is already registered." % sector_path)

        logging.info("writing metadata...")
        with open(os.path.join(sector_path, CHADOW_METADATA), "w+") as metadata:
            metadata.write(sector_name)
        
        config["libraries"][library]["sectors"][sector_name] = sector_path
        logging.info("Updating cfg...")
        __write_cfg(
            config, config_filename,
            "Created sector %s for library %s at %s." % (sector_name, library, sector_path)
        )
    except FileNotFoundError:
        # Metadata file is opened as "w+" so we can be confident that this is
        # from opening the config file.
        import traceback
        traceback.print_exc()
        logging.error("config file not found. Is chadow installed properly?")
        exit(1)

if __name__ == "__main__":
    cli()
