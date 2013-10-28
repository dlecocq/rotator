Rotator
=======
Piped log rotation

It can sometimes be tricky and invasive to implement log rotation, especially if
there are forked processes involved. What's significantly easier is writing logs
to `stdout` and having another utility manage where those logs live.

In particular, we encoutered a problem where we wanted to track the logs of a
process that forked child process to do work. This _really_ makes life
complicated for log rotation, and so the easiest way to deal with it was to have
every process write to `stdout`, inherited from the parent process, and let a
separate utility deal with it.

Usage
=====
There are three modes that `rotator` supports: `signaled`, `watched` and
`rotated`. They're all implemented as subcommands of the `rotator` binary.

Signaled
--------
In `signaled` mode, a configurable signal can be sent to the process to indicate that the file needs to be reopened:

```bash
my-awesome-program | rotator signaled /path/to/log --sig USR1
```

From another process:

```bash
# Rotate the file
mv /path/to/log /to/somewhere/else
kill -USR1 <pid>
```

Rotated
-------
In `rotated` mode, the utility does all the rotation for itself making use of
the provided `size` and `count`. For example, this would keep up to 5 logs files
at `/path/to/log.{1,2,3,4,5}`:

```bash
my-awesome-program | rotator rotated /path/to/log --size 1MB --count 5
```

Watched
-------
This mode actually checks whether the path's `inode` has changed, and thus has
to be reopened. It's a pretty expensive operation, but it is available:

```bash
my-awesome-program | rotator watched /path/to/log
```

In order to do the rotation in this case:

```bash
# The utility automatically detects that the path has moved
mv /path/to/log /to/somewhere/else
```

Installation
============
You can install `rotator` from `pip`:

```bash
sudo pip install rotator
```

Or from github:

```bash
git clone https://github.com/dlecocq/rotator
cd rotator
sudo python setup.py install
```