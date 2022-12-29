from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union
from typing_extensions import TypedDict

import click
import enum
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
# We add a metadata dotfile to the media path to ensure that a media path can't
# be part of more than one sector.
CHADOW_METADATA: str = ".chadow-metadata"
PATH_SEPARATOR_REPLACEMENT: str = "+"

@enum.unique
class ExitCodes(enum.Enum):
    """
    Invalid config means there is something structurally wrong with the config.
    For example, it is an invalid JSON document. Or when an expected field is
    not present.
    """
    INVALID_CONFIG = 100
    CONFIG_NOT_FOUND = 101
    METADATA_NOT_FOUND = 102
    """
    State conflict means that although the config passed validation, there is
    something _semantically_ wrong with it. For example, we are told to create
    a key that already exists, or a user-defined key maps to an unexpected data
    structure (list vs. dict).
    """
    STATE_CONFLICT = 103
    INVALID_ARG = 104
    PERMISSIONS_PROBLEM = 105
    OS_ERROR = 106

# Lists things that are NOT in this sector but are in other sectors.
SectorDiffBin = List[
    # 0 - the sector where this item can be found
    # 1 - the actual item identifier
    Tuple[str, str]
]
SectorDiffMapping = Dict[str, SectorDiffBin]

class SectorComparisonReport(object):

    def __init__(
        self,
        largest_sector: Optional[Tuple[str, int]],
        smallest_sector: Optional[Tuple[str, int]],
        # dict key is the name of the sector the diff bin is describing
        diff_bins: Optional[SectorDiffMapping]
    ):
        self.largest_sector = largest_sector
        self.smallest_sector = smallest_sector
        self.diff_bins = diff_bins

IndexItem = Union[str, "DirectoryIndex"]

class DirectoryIndex(object):

    def __init__(
        self,
        subdir_path: Optional[str]=None,
        is_top_level: bool=True,
        version: Optional[str]=VERSION
    ) -> None:
        self.version: Optional[str] = version if is_top_level else None
        # FIXME: Prevent acyclic structures
        self.index: Set[IndexItem] = set()
        self.is_top_level = is_top_level
        self.subdir_path: Optional[str] = None
        if not is_top_level:
            self.subdir_path = subdir_path

    def __eq__(self, other):
        return all((
            self.is_top_level == other.is_top_level,
            self.index == other.index,
            self.subdir_path == other.subdir_path
        ))

    def __hash__(self):
        def index_key(i1: IndexItem):
            if isinstance(i1, DirectoryIndex):
                if i1.is_top_level:
                    raise Exception("Can't sort a top-level index.")
                return "Z-%s" % i1.subdir_path

            return i1

        return hash((
            self.is_top_level, tuple(sorted(self.index, key=index_key)), self.subdir_path
        ))

    def add_to_index(self, item: IndexItem):
        if item is not None:
            self.index.add(item)
        else:
            logging.warn("Asked to index a None object!")

    def __to_dict(self) -> dict:
        dict_rep: Dict[str, Any] = {}
        if self.is_top_level:
            dict_rep["version"] = self.version
        elif self.subdir_path is not None:
            dict_rep["subdir_path"] = self.subdir_path
        else:
            # This should never happen but we are tolerant about it
            logging.warn("None passed as subdirectory name. Coercing to blank (which is still unacceptable)!")
            dict_rep["subdir_path"] = ""
        
        dict_rep["index"] = []

        for item in self.index:
            if isinstance(item, str):
                dict_rep["index"].append(item)
            else:
                dict_rep["index"].append(item.__to_dict())

        return dict_rep

    def to_json(self) -> str:
        return json.dumps(self.__to_dict())
    
    @staticmethod
    def construct_from_dict(d: Dict, dirpath: Optional[str]=None) -> "DirectoryIndex":
        index = DirectoryIndex(
            version=d.get("version"),
            subdir_path=d.get("subdir_path") or dirpath,
            is_top_level=d.get("version") is not None
        )

        for item in d["index"]:
            if isinstance(item, str):
                index.add_to_index(item)
            else:
                index.add_to_index(DirectoryIndex.construct_from_dict(item))

        return index

def make_filename_diffbins(sector_sets: Dict[str, Set[str]]) -> SectorDiffMapping:
    """
    This is the filename comparator.
    """
    mapping: SectorDiffMapping = {sector:[] for sector in sector_sets}
    for sector in sector_sets:
        sector_names = set(sector_sets.keys())
        sector_names.remove(sector)
        for other_sector in sector_names:
            only_in_sector = sector_sets[sector].difference(sector_sets[other_sector])
            only_in_other_sector = sector_sets[other_sector].difference(sector_sets[sector])

            for item in only_in_sector:
                mapping[other_sector].append((sector, item))

            for item in only_in_other_sector:
                mapping[sector].append((other_sector, item))

    return mapping

@click.group()
def cli():
    pass

DataLibrary = TypedDict(
    "DataLibrary",
    {
        "sectors": Dict[str, List[str]],
        "comparator": str
    }
)
ChadowConfig = TypedDict(
    "ChadowConfig",
    {
        "version": str,
        "libraryMapping": Dict[str, DataLibrary]
    }
)

def __version_check(cfg_dict: ChadowConfig):
    """
    Side-effect-ful version check: check config version and inform user as
    necessary.
    """
    version = cfg_dict.get("version")
    if version and version != VERSION:
        logging.warning("loading a chadow config from an old version.")
    elif not version:
        logging.warning("config does not specify a version.")

def __config_load(full_config_name: str) -> ChadowConfig:
    """
    Load the config from the specified filename. Also performs verification that
    the config is valid.
    """
    config: ChadowConfig = {"version": VERSION, "libraryMapping": {}}
    with open(full_config_name, "r") as config_file:
        config = json.load(config_file)
        __version_check(config)

    return config

def __write_cfg(updated_config: ChadowConfig, config_filename: str, log_mesg: str):
    with open(config_filename, "w") as config_file:
        json.dump(updated_config, config_file)
    
    logging.info(log_mesg)

def __normalize_path_separator(path: str):
    return path.replace(os.path.sep, PATH_SEPARATOR_REPLACEMENT) 

def __denormalize_index_dir(index_dir: str):
    return index_dir.replace(PATH_SEPARATOR_REPLACEMENT, os.path.sep)

def make_sector_dirname(library_name: str, sector_name: str):
    return os.path.join(APP_ROOT, library_name, sector_name)

def __make_sectorpath_dirname(
    library_name: str, sector_name: str, sector_path: str
):
    return os.path.join(
        APP_ROOT, library_name, sector_name, __normalize_path_separator(sector_path)
    )

def make_default_lib(comparator: str) -> DataLibrary:
    return {
        "sectors": {},
        "comparator": comparator
    }

@cli.command()
@click.argument("name")
@click.option("--force", is_flag=True, default=False, help="Set to force recreation of a corrupted library")
def createlib(name: str, force: bool):
    def __createlib(cfg_contents: str, comparator="filename"):
        config = json.loads(cfg_contents)
        __version_check(config)
        existing_libraries = config.get("libraryMapping", {})

        if name in existing_libraries:
            logging.error("specified name is already taken. Delete name first if you really want to use this name.")
            exit(ExitCodes.STATE_CONFLICT.value)
        else:
            existing_libraries[name] = make_default_lib(comparator)

        config["libraryMapping"] = existing_libraries
        return config

    config_filename = os.path.join(APP_ROOT, CONFIG_NAME)
    updated_config = None
    try:
        with open(config_filename, "r") as config_file:
            logging.info("Writing config file: %s" % config_filename)
            updated_config = __createlib(config_file.read())
        __write_cfg(updated_config, config_filename, "Created new lib: %s" % name)
        os.mkdir(os.path.join(APP_ROOT, name))
    except json.decoder.JSONDecodeError:
        if force:
            fresh_config = json.dumps({
                "version": "%s" % VERSION,
                "libraryMapping": {}
            })
            with open(config_filename, "w") as config_file:
                logging.warning("Forced to recreate corrupted library.")
                config_file.write(fresh_config)
                config_file.flush()
                updated_config = __createlib(fresh_config)
            __write_cfg(updated_config, config_filename, "Created new lib: %s" % name)
            os.mkdir(os.path.join(APP_ROOT, name))
        else:
            logging.error("Corrupted config file. You can either fix it manually or call createlib with --force.")
            exit(ExitCodes.INVALID_CONFIG.value)

@cli.command()
def lslib():
    config_filename = os.path.join(APP_ROOT, CONFIG_NAME)
    try:
        cfg = __config_load(config_filename)
        libs = cfg["libraryMapping"].keys()
        print("\n".join(libs))
    except json.decoder.JSONDecodeError:
        logging.error("Can't read config, invalid JSON. Forcing creation of a new library would recreate a valid config but will destroy existing data.")
        exit(ExitCodes.INVALID_CONFIG.value)

@cli.command()
@click.argument("name")
def deletelib(name: str):
    try:
        config_filename = os.path.join(APP_ROOT, CONFIG_NAME)
        with open(config_filename, "rw") as config_file:
            config = json.load(config_file)
            __version_check(config)
            existing_libraries = config.get("libraryMapping", {})

            if name in existing_libraries:
                del existing_libraries[name]
                __write_cfg(config, config_filename, "Deleted library: %s" % name)
            else:
                logging.error("asked to delete a nonexistent library.")
                exit(ExitCodes.STATE_CONFLICT.value)
    except FileNotFoundError:
        logging.error("config file not found. Is chadow installed properly?")
        exit(ExitCodes.CONFIG_NOT_FOUND.value)
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
        exit(ExitCodes.INVALID_ARG.value)

    try:
        config_filename = os.path.join(APP_ROOT, CONFIG_NAME)
        config = __config_load(config_filename)
        library_sectors = config["libraryMapping"][library]["sectors"]

        if library_sectors.get(sector_name) is not None:
            logging.error("Asked to register a sector that already exists")
            if type(library_sectors[sector_name]) is not list:
                logging.warn("Pre-existing sector might be corrupted.")

            exit(ExitCodes.STATE_CONFLICT.value)
        else:
            library_sectors[sector_name] = []
            try:
                sector_dirname = make_sector_dirname(library, sector_name)
                os.mkdir(make_sector_dirname(library, sector_dirname))
                logging.info("Created sector index directory: %s" % sector_dirname)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    logging.info("Sector index directory already exists.")
                else:
                    logging.error("Unable to create sector index directory.")
                    exit(ExitCodes.OS_ERROR.value)
            except PermissionError:
                logging.error("No permission to create sector index directory.")
                exit(ExitCodes.PERMISSIONS_PROBLEM.value)
            __write_cfg(
                config, config_filename,
                "Created sector %s for library %s." % (sector_name, library)
            )
    except FileNotFoundError:
        logging.error("config file not found. Is chadow installed properly?")
        exit(ExitCodes.CONFIG_NOT_FOUND.value)
    except AttributeError:
        logging.error("Library sectors for %s is not readable! Please reformat." % library)
        exit(ExitCodes.STATE_CONFLICT.value)

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
        exit(ExitCodes.INVALID_ARG.value)

    try:
        config_filename = os.path.join(APP_ROOT, CONFIG_NAME)
        config = __config_load(config_filename)
        metadata_path = os.path.join(sector_path, CHADOW_METADATA)
        if os.path.isfile(metadata_path):
            logging.error("specified path %s is already registered." % sector_path)
            exit(ExitCodes.STATE_CONFLICT.value)

        try:
            with open(metadata_path, "w+") as metadata:
                metadata.write(sector_name)
                metadata.flush()
        except FileNotFoundError:
            logging.error("metadata can't be opened. Please check the sector path provided.")
            exit(ExitCodes.METADATA_NOT_FOUND.value)
        except PermissionError:
            logging.error("can't open metadata file. Are you sure we have the proper permissions to the path?")
            exit(ExitCodes.PERMISSIONS_PROBLEM.value)
        
        if config["libraryMapping"][library].get("sectors") is not None:
            if not os.path.isdir(make_sector_dirname(library, sector_name)):
                logging.error("State conflict: missing directory for sector %s." % sector_name)
                exit(ExitCodes.STATE_CONFLICT.value)
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
            exit(ExitCodes.STATE_CONFLICT.value)
    except FileNotFoundError as fnfe:
        logging.error("config file not found. Is chadow installed properly?")
        logging.error(fnfe, exc_info=True)
        exit(ExitCodes.CONFIG_NOT_FOUND.value)

@cli.command()
@click.argument("library")
@click.argument("sector_name")
@click.argument("sector_path")
@click.option("--verbose", is_flag=True, default=False, help="verbose will output the index written as a text stream")
def index(library: str, sector_name: str, sector_path: str, verbose: bool=False):
    logging.info("Indexing %s.%s.%s..." % (library, sector_name, sector_path))
    config: ChadowConfig = {"version": VERSION, "libraryMapping": {}}

    try:
        config_filename = os.path.join(APP_ROOT, CONFIG_NAME)
        config = __config_load(config_filename)
    except FileNotFoundError:
        logging.error("config file not found. Is chadow installed properly?")
        exit(ExitCodes.CONFIG_NOT_FOUND.value)
    except PermissionError:
        logging.error("can't open config file. Are you sure we have the proper permissions for it?")
        exit(ExitCodes.PERMISSIONS_PROBLEM.value)

    # This is a pre-emptive check. Technically, nothing stops us from creating
    # an index even if it is not registered in the config. However, this would
    # singify a state discrepancy---the directory to save the index in probably
    # does not exist! We could still reach this conclusion later but checking
    # here saves us an expensive operation.
    try:
        sector = config["libraryMapping"][library]["sectors"][sector_name]
        if sector_path not in sector:
            logging.error("%s is not a registered media in this sector." % sector_path)
            exit(ExitCodes.STATE_CONFLICT.value)
    except KeyError:
        logging.error("Config invalid for given arguments.")
        exit(ExitCodes.INVALID_CONFIG.value)

    root_index = DirectoryIndex(sector_path, is_top_level=True)
    parents = {}
    # Use os.walk instead of os.listdir so that full path construction is
    # handled for free.
    for root, dirs, files in os.walk(sector_path):
        dir_index = (
            root_index
            if root == sector_path else
            DirectoryIndex(root.split(os.sep)[-1], is_top_level=False)
        )

        for _file in files:
            dir_index.add_to_index(_file)

        for _dir in dirs:
            this_path = os.path.join(root, _dir)
            parents[this_path] = dir_index
        
        if parents.get(root):
            parents[root].add_to_index(dir_index)

    sector_path_dir = __make_sectorpath_dirname(library, sector_name, sector_path)
    with open(os.path.join(sector_path_dir, "index.json"), "w+") as path_index:
        logging.info("Writing index.json to %s" % sector_path_dir)
        path_index.write(root_index.to_json())

    if verbose:
        print(str(root_index.to_json()))

if __name__ == "__main__":
    cli()
