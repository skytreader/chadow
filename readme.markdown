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
