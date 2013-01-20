XYZ
=====

XYZ is a system for generating standalone application packages.
XYZ packages are designed to be run by any user from any location on the filesystem with minimal dependencies.
This contrasts from most system packaging systems which generally require system wide installation (and root access to install the package).
XYZ enables multiple versions of the same packaged application to be installed on a system.
XYZ is primarily designed for use within development projects that require a specific set of tools (such as embedded systems development toolchains).
Usually a package itself does not required any run-time depdences, so it should be possible to install packages without requiring many dependent packages.


Prerequisites
--------------

The goal of XYZ packages is that a user shouldn't need to install any additional tools to use a given package.
This generally means that the packaged applications are mostly statically compiled, or ship with any required shared libraries.
Of course the usual dynamic vs static library trade-offs apply here, so if you prefer the benefits of shared libraries this system isn't for you.
At some level assumptions about the underlying platform must be made.
In general common `standard` libraries are assumed to exist on the platform. Including:

* libc (libSystem on OS X).
* libm
* libiconv (include in glibc on GNU/Linux)
* libncurses
* libz

Some packages on OS X may also depend on standard CoreFramework APIs.
Dependencies on other shared libraries, or filesystem paths are avoided to the largest extent possible.
Unfortunately there is a lot of software that makes a lot of assumptions about being able to find files in certain fixed locations. The design approach of XYZ is to attempt to fix such assumptions in the source code by whatever means necessary. In some cases, this results in a loss of functionality.


Build Prerequisites
---------------------

Building XYZ packages is not as simple as just using them.
A *standard* development environment is required for building the packages themselves.
At some point it would be ideal if all the build dependencies could be satisfied by XYZ packages, however this will require packaging a large number of utilities and toolchains.

### Python 3

The core packaging utility is written in Python 3.
The first iteration of this tool started as a POSIX compliant shell script for maximum portability, however as the tool has increased in functionality this approach became cumbersome.
Not all systems have Python 3 installed by default, so users should be especially aware of this dependencies.

### git

The source for all packages is stored on github.
`git` and a suitable network connection to github is required.


Platforms
-----------

The goal is to support OS X, GNU/Linux and Windows.
Currently packages are primarily available for OS X and GNU/Linux.


Package Format
----------------

Currently the package format is a simple compressed tape archive (tar) file.
Usage is as simple as un-archiving in your preferred location.
To use the package either directly reference the applications, or add the appropriate directory to your `PATH` environment
In general different packages can be un-archived in the same directory as they do not contain conflicting files.
The package format may change in the future, however the goal is to keep it simple to avoid the need for heavy-weight installers.

Each tar file has a listing file that is stored in
`share/xyz/<pkg-variant-name>`. The listing includes a header with
version information, followed by a list of files in the package
along with a hash of the file contents.


Packaging Directories
---------------------

The following directories are used during the packaging process.
They are all ignored by git.

### `source`

All package source is pulled from a git repository.
This is different from some other systems that maintain explicit patch sets.
Any necessary bug-fixes or customisations are maintained within a git repository.

### `devtree`

This contains temporarily installed packages for development use.
For example, when building a gcc toolchain this contains libraries such as libgmp, etc.
This does not necessarily include only installed xyz packages.
Some development libraries are simply directly installed in to this directory without intermediate packaging.

### `build`

Packages are built within the build directory.
This is generally where `configure` and `make` are executed from.

### `install`

Packages are installed to this directory before being packaged.
This is generally the destination of `make install`.

### `release`

Location of complete packages.


Usage
------

To build a package:

% ./xyz.py <pkgname> [--force]

This will build the package and any of its dependencies. Generally if you execute this twice in a row it will rerun the `make` part, but avoid reconfiguring, or reinstalling dependencies. `--force` will conduct a fully fresh build.

To clean up your entire working directory:

% ./xyz.py --clean

To clean up the working directory, and any releasable packages:

% ./xyz.py --clean-release

To ensure that there are no conflicts in the packages:

% ./xyz.py --check-packages


Versioning
-----------

Currently package versioning is unspecified.


Similar Systems
----------------

Th following systems have provided some form of design inspiration and ideas towards this project:

* Homebrew
* dpkg / apt-get
* RPM / yum
* MinGW


Reproducible builds
---------------------

One of the goals of XYZ is that it should be simple to reproduce builds easily.
To achieve this the tools aims to minimize the extent to which environmental concerns may impact on the build.
Some of the techniques used are:

### `-Z` linker flag (OS X only)

The `-Z` flag disables the standard linker library search path.
Specifically, this stops the linker searching `/usr/local/lib`, which may contain any number of uncontrolled libraries.
Use of this flag avoids inadvertently using these libraries.

### `-search_paths_first` linker flag. (OS X only)

On OS X the standard search path is unintuitive.
The linker tries very hard to use dynamic libraries over static libraries, and will search all paths for a dynamic library before falling back to static libraries.
The `-search_paths_first` linker flag changes this behaviour so that the linker searches for dynamic or static library in each part of the search path.

### Minimal `PATH` environment set

A standard `PATH` environment variable is used to avoid any user specific binaries.
Currently this is set to `/usr/bin:/bin`.

### Removing .la files

Despite protestations to the contrary `.la` files are generally not needed by the linke, however their hardcoded paths can really mess things up.
By default `.la` files are removed post-installation.

### Removing duplicate info files

There are some info files that are installed by multiple packages.
Unfortunately these files are actually different! As the most
practical measure, these files are removed from each package that
installs them.

### Using an improved texinfo implementation

The latest version of texinfo (4.13a) has a deficiency around the way in which indexes are sorted. Indexes are sorted using an unstable sort (qsort), which leads to non-deterministic generation.

### Fixing Python hash seed.

As described in http://benno.id.au/blog/2013/01/15/python-determinism Python hashing can affect the marshalled source code, leading to non-deterministic output of `.pyc` and `.pyo` files.

### Standard `umask` used during builds.

The `umask` can affect the output packages as described here http://benno.id.au/blog/2013/01/09/autopedant.
To avoid such problems a standard `umask` is used when generating packages.

### Configure with minimal dependencies

As a general rule, reducing the number of dependencies makes things more reliable and repeatable.
Unless features are absolutely critical we try to avoid configuring optional things.

### Use of `--prefix` and `--exec-prefix`

Many source packages support specifying a `prefix` and an `exec-prefix`.
Platform specific files (should) then be placed in the `exec-prefix`, while non-platform dependent files (should) reside within `prefix`.
This approach is used to avoid having duplicate files for no good reason.
However, not all packages correctly respect this, and as a result it is sometimes necessary to set `prefix` to be `exec-prefix` to avoid
having collisions.


Writing the rules
-------------------

Packages are described by an appropriate rules description.
The rules description is a standard python module placed in the `rules` directory.
The name of the description should be `<pkg_name>.py`.
The package python file should export a module level variable `rules`.
The `rules` object should be an instance of a subclass of the `BuildProtocol` class.
See the `BuildProtocol` class documentation strings for details on the various methods that should be provied.


Variations
------------

Each package can support multiple *variations*.
Variations enable multiple release packages from a single source package.
For example, the `gcc` source package may support multiple different cross-compile targets.


Future Work
--------------

* Versioning specification
* Disconnected mode: provide a command line argument to specify no network activity.
* Automatically updating source git repos. Currently not updated after initial clone.
