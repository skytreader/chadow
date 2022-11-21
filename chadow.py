from typing import Any, Dict, List, Optional, Set, Union

import click
import errno
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_version() -> str:
    with open("VERSION") as v:
        vlist = list(v)
        if len(vlist) > 1:
            logging.warn("The version file has more than one line.")

        for line in vlist:
            return line.strip()

    # The only time execution will get to this is when there is not a single
    # line to read from the version file.
    raise Exception("Version file is empty!")

VERSION: str = get_version()
APP_ROOT: str = os.path.expanduser("~/.chadow")
CONFIG_NAME: str = "config.json"
CHADOW_METADATA: str = ".chadow-metadata"
PATH_SEPARATOR_REPLACEMENT: str = "+"

# Exit codes
CONFIG_NOT_FOUND = 1
METADATA_NOT_FOUND = 2
STATE_CONFLICT = 3
INVALID_ARG = 4
PERMISSIONS_PROBLEM = 5
OS_ERROR = 6

class DirectoryIndex(object):

    def __init__(
        self,
        subdir: Optional[str]=None,
        is_top_level: bool=True,
        version: str=VERSION
    ) -> None:
        self.version: str = version
        # FIXME: Prevent acyclic structures
        self.index: Set[Union[str, "DirectoryIndex"]] = set()
        self.is_top_level = is_top_level
        self.subdir: Optional[str] = None
        if not is_top_level:
            self.subdir = subdir

    def __eq__(self, other):
        return all((
            self.is_top_level == other.is_top_level,
            self.index == other.index,
            self.subdir == other.subdir
        ))

    def __hash__(self):
        return hash((
            self.is_top_level, tuple(self.index), self.subdir
        ))

    def add_to_index(self, item: Union[str, "DirectoryIndex"]):
        if item is not None:
            self.index.add(item)
        else:
            logging.warn("Asked to index a None object!")

    def __to_dict(self) -> dict:
        dict_rep: Dict[str, Any] = {}
        if self.is_top_level:
            dict_rep["version"] = self.version
        elif self.subdir is not None:
            dict_rep["subdir"] = self.subdir
        else:
            # This should never happen but we are tolerant about it
            logging.warn("None passed as subdirectory name. Coercing to blank (which is still unacceptable)!")
            dict_rep["subdir"] = ""
        
        dict_rep["index"] = []

        for item in self.index:
            if isinstance(item, str):
                dict_rep["index"].append(item)
            else:
                dict_rep["index"].append(item.__to_dict())

        return dict_rep

    def to_json(self) -> str:
        return json.dumps(self.__to_dict())

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

def __config_check(full_config_name: str):
    config: Dict = {}
    with open(full_config_name) as config_file:
        config = json.load(config_file)
        __version_check(config)

    return config

def __write_cfg(updated_config: Dict[str, str], config_filename: str, log_mesg: str):
    with open(config_filename, "w") as config_file:
        json.dump(updated_config, config_file)
    
    logging.info(log_mesg)

def __normalize_path_separator(path: str):
    return path.replace(os.path.sep, PATH_SEPARATOR_REPLACEMENT) 

def __denormalize_index_dir(index_dir: str):
    return index_dir.replace(PATH_SEPARATOR_REPLACEMENT, os.path.sep)

def __make_sector_dirname(library_name: str, sector_name: str):
    return os.path.join(APP_ROOT, library_name, sector_name)

def __make_sectorpath_dirname(
    library_name: str, sector_name: str, sector_path: str
):
    return os.path.join(
        APP_ROOT, library_name, sector_name, __normalize_path_separator(sector_path)
    )

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
        logging.info("Writing config file: %s" % config_filename)
        with open(config_filename, "r") as config_file:
            updated_config = __createlib(config_file)
        __write_cfg(updated_config, config_filename, "Created new lib: %s" % name)
        os.mkdir(os.path.join(APP_ROOT, name))
    except json.decoder.JSONDecodeError:
        # Config file is malformed json. Maybe a botched install. But let's be
        # forgiving anyway and reformat the malformed config.
        with open(config_filename, "rw+") as config_file:
            logging.warning("unreadable json in config file. Reformatting.")
            config_file.write('{"version": "%s", "libraryMapping": {}}' % VERSION)
            config_file.flush()
            updated_config = __createlib(config_file)
        __write_cfg(updated_config, config_filename, "Created new lib: %s" % name)
        os.mkdir(os.path.join(APP_ROOT, name))

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
    finally:
        try:
            os.rmdir(os.path.join(APP_ROOT, name))
        except FileNotFoundError:
            logging.warn(
                "%s does not exist. Possible data loss condition!" %
                os.path.join(APP_ROOT, name)
            )

@cli.command()
@click.argument("library")
@click.argument("sector_name")
def regsector(library: str, sector_name: str):
    logging.info("Registering sector %s for library %s." % (sector_name, library))
    if os.path.sep in sector_name:
        logging.error("sector_name could not contain the path separator %s" % os.path.sep)
        exit(INVALID_ARG)

    try:
        config_filename = os.path.join(APP_ROOT, CONFIG_NAME)
        config = __config_check(config_filename)
        library_sectors = config["libraryMapping"][library]["sectors"]

        if library_sectors.get(sector_name):
            logging.error("Asked to register a sector that already exists")
            exit(STATE_CONFLICT)
        else:
            library_sectors[sector_name] = []
            try:
                sector_dirname = __make_sector_dirname(library, sector_name)
                os.mkdir(__make_sector_dirname(library, sector_dirname))
                logging.info("Created sector index directory: %s" % sector_dirname)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    logging.info("Sector index directory already exists.")
                else:
                    logging.error("Unable to create sector index directory.")
                    exit(OS_ERROR)
            except PermissionError:
                logging.error("No permission to create sector index directory.")
                exit(PERMISSIONS_PROBLEM)
            __write_cfg(
                config, config_filename,
                "Created sector %s for library %s." % (sector_name, library)
            )
    except FileNotFoundError:
        logging.error("config file not found. Is chadow installed properly?")
        exit(CONFIG_NOT_FOUND)

@cli.command()
@click.argument("library")
@click.argument("sector_name")
@click.argument("sector_path")
def regmedia(library: str, sector_name: str, sector_path: str):
    # TODO Make sure this is atomic.
    logging.info("asked to register media %s in sector %s." % (sector_path, sector_name))

    if PATH_SEPARATOR_REPLACEMENT in sector_path:
        logging.error(
            "sector_path cannot have the %s character!\nGiven: %s" % (
                PATH_SEPARATOR_REPLACEMENT, sector_path
            )
        )
        exit(INVALID_ARG)

    try:
        config_filename = os.path.join(APP_ROOT, CONFIG_NAME)
        config = __config_check(config_filename)
        metadata_path = os.path.join(sector_path, CHADOW_METADATA)
        if os.path.isfile(metadata_path):
            logging.error("specified path %s is already registered." % sector_path)
            exit(STATE_CONFLICT)

        try:
            with open(os.path.join(sector_path, CHADOW_METADATA), "w+") as metadata:
                metadata.write(sector_name)
                metadata.flush()
        except FileNotFoundError:
            logging.error("metadata can't be opened. Please check the sector path provided.")
            exit(METADATA_NOT_FOUND)
        except PermissionError:
            logging.error("can't open metadata file. Are you sure we have the proper permissions to the path?")
            exit(PERMISSIONS_PROBLEM)
        
        if config["libraryMapping"][library].get("sectors"):
            if not os.path.isdir(__make_sector_dirname(library, sector_name)):
                logging.error("State conflict: missing directory for sector %s." % sector_name)
                exit(STATE_CONFLICT)
            os.mkdir(__make_sectorpath_dirname(library, sector_name, sector_path))
            config["libraryMapping"][library]["sectors"][sector_name].append(sector_path)
            __write_cfg(
                config, config_filename,
                "Registered media for library %s at sector %s at path %s." % (
                    library, sector_name, sector_path
                )
            )
        else:
            logging.error("Sector %s not found. Are you sure you have registered this sector before?" % sector_name)
            exit(STATE_CONFLICT)
    except FileNotFoundError as fnfe:
        logging.error("config file not found. Is chadow installed properly?")
        logging.error(fnfe, exc_info=True)
        exit(CONFIG_NOT_FOUND)

@cli.command()
@click.argument("library")
@click.argument("sector_name")
@click.argument("sector_path")
def index(library: str, sector_name: str, sector_path: str):
    logging.info("Indexing %s.%s.%s..." % (library, sector_name, sector_path))
    config: Dict = {}

    try:
        config_filename = os.path.join(APP_ROOT, CONFIG_NAME)
        config = __config_check(config_filename)
    except FileNotFoundError:
        logging.error("config file not found. Is chadow installed properly?")
        exit(CONFIG_NOT_FOUND)
    except PermissionError:
        logging.error("can't open config file. Are you sure we have the proper permissions for it?")
        exit(PERMISSIONS_PROBLEM)

    dir_index = DirectoryIndex(sector_path, is_top_level=True)
    subdir_traversal = [sector_path]
    is_top_level = True
    parents = {}

    while subdir_traversal:
        curdir = subdir_traversal.pop()

        if is_top_level:
            curindex = dir_index
            is_top_level = False
        else:
            curindex = DirectoryIndex(
                subdir=curdir.split(os.sep)[-1],
                is_top_level=False
            )

        # Use os.walk instead of os.listdir so that full path construction is
        # handled for free.
        for root, dirs, files in os.walk(curdir):
            for _file in files:
                curindex.add_to_index(_file)

            for _dir in dirs:
                subdir_traversal.append(os.path.join(root, _dir))
                parents[os.path.join(root, _dir)] = curindex

            # one run only
            break
        
        if parents.get(curdir):
            parents[curdir].add_to_index(curindex)

    sector_path_dir = __make_sectorpath_dirname(library, sector_name, sector_path)
    with open(os.path.join(sector_path_dir, "index.json"), "w+") as path_index:
        logging.info("Writing index.json to %s" % sector_path_dir)
        path_index.write(dir_index.to_json())

if __name__ == "__main__":
    cli()
