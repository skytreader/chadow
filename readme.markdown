# chadow

Scenario: A very large library of data (like, say, a big bunch of photos) is
backed-up redundantly across _n_ storage sectors. Each storage sector in turn
maybe comprised of _m_ different storage media. Now, you want to ensure that
the file back-ups are consistent and complete across your storage sectors.

Explicitly built for Linux (Ubuntu) for the meantime.

## Installation and Quickstart

Install via the included `install` script. This requires virtualenv goodies as
installed via [virtualenv-burrito](https://github.com/brainsik/virtualenv-burrito).

Create a new data library to track with the `createlib` command.

Register a new storage sector with the `regsector` command. This command assumes
that the physical storage medium they are mapped to, when mounted on your
computer, mount to distinct special files (i.e., in the loosest terms, don't
have two flash drives with the same name because then they will collide on the
same `/media/user/flash_drive_name` path).
