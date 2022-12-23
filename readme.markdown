# chadow

Idea:

- Each **library** is a collection of data---text, video, images, etc. There is
a canonical set of this data.
- Each **sector** in a library replicates the _whole_ data set.
- A sector is divided across different storage **media**. The union of all the
contents in each storage medium should be similar across sectors.

chadow helps to ensure this consistency.

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

Having installed `requirements.txt`, you can test by simply running the
`chadow_test.py` file in this repo.

The test script also features some convenience params which you can view by
running `python chadow_test.py -h`.
