# chadow

Scenario: A very large library of data (like, say, a big bunch of photos) is
backed-up redundantly across _n_ storage sectors. Each storage sector in turn
maybe comprised of _m_ different storage media. Now, you want to ensure that
the file back-ups are consistent and complete across your storage sectors.

Explicitly built for Linux (Ubuntu) for the meantime.

## Installation and Quickstart

Install via the included `install` script. This requires virtualenv goodies as
installed via [virtualenv-burrito](https://github.com/brainsik/virtualenv-burrito).

### Commands

All prefixed by `python ~/.chadow/chadow.py`...

    createlib LIBRARY_NAME

Create a new data library to track with the `createlib` command.

    regsector LIBRARY_NAME SECTOR_NAME

Register a new storage sector with the `regsector` command. Remember that a
sector is a collection of different storage media which, when taken together
comprises a library.

    regmedia LIBRARY_NAME SECTOR_NAME /path/to/mount

To register actual storage media to your sectors, use the `regmedia` command.
This command assumes that the physical storage medium they are mapped to, when
mounted on your computer, mount to distinct special files (i.e., in the loosest
terms, don't have two flash drives with the same name because then they will
collide on the same `/media/user/flash_drive_name` path).

    index LIBRARY_NAME SECTOR_NAME /path/to/mount

Index a media path to get a "snapshot" of its contents. This will be used to
compare the consistency of sectors in the library.

## Testing

There are two testing modes: full testing and quick testing.

Full testing incorporates a full installation and uninstallation before and
after each test case. In this sense, we are sure that the commands work as
expected from a clean install. However, installation means recreating the
virtualenv on which chadow is supposed to run.

Quick testing, on the other hand, will not recreate the virtualenv everytime. In
fact, quick testing will not rely on a virtualenv anytime; the Docker image used
to do quick testing has the Python dependencies specified "natively".

This allows for a faster feedback loop during development (just run quick tests)
but the changes are still tested thoroughly by CI, which _always_ runs full
testing.

Every effort is done to keep the two testing environments similar. The only
notable difference is that the Docker image for full testing inherits from
Ubuntu (the target platform of chadow) while quick testing inherits from Debian/

### Running quick tests

Just build the Docker image locally,

    docker build -t chadow:quicktest -f Dockerfile-quicktest .

Then invoke

    ./dockertest quick
