#!/usr/bin/env python3
"""
A tool for building relocatable packages of UNIX applications.

See README.md for details.
"""
import os
import sys
import platform
import calendar
import logging
import shutil
import tarfile
import hashlib
from contextlib import contextmanager

# Location where all the git repo where the source is stored.
SOURCE_REPO_PREFIX = 'git://github.com/BreakawayConsulting/'

# Create a module alias. This allows plugs to import xyz without
# creating a new module instance.
sys.modules['xyz'] = sys.modules[__name__]

logger = logging.getLogger('xyz')
logging.basicConfig(level=logging.INFO)

BASE_TIME = calendar.timegm((2013, 1, 1, 0, 0, 0, 0, 0, 0))


def man_remove_header(m):
    tmp = '{}.tmp'.format(m)
    with open(m) as inp, open(tmp, 'w') as outp:
        first = True
        for l in inp:
            if first:
                first = False
                if 'generated' in l:
                    continue
            outp.write(l)
    os.rename(tmp, m)


def tar_info_filter(tarinfo):
    tarinfo.uname = 'xyz'
    tarinfo.gname = 'xyz'
    tarinfo.mtime = BASE_TIME
    tarinfo.uid = 1000
    tarinfo.gid = 1000
    return tarinfo


def tar_bz2(output, tree):
    with tarfile.open(output, 'w:bz2', format=tarfile.GNU_FORMAT) as tf:
        with chdir(tree):
            tf.add('.', filter=tar_info_filter)


class UsageError(Exception):
    """This exception is caught 'cleanly' when running as a script.

    It allows code to easily return usage errors to the user.

    """


def ensure_dir(path):
    """Ensure that a specific directory exists."""
    return os.makedirs(path, exist_ok=True)


def touch(path):
    """Create an empty file (just like the unix touch command)."""
    open(path, 'w').close()


@contextmanager
def chdir(path):
    """Current-working directory context manager. Makes the current
    working directory the specified `path` for the duration of the
    context.

    Example:

    with chdir("newdir"):
        # Do stuff in the new directory
        pass

    """
    cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(cwd)


@contextmanager
def umask(new_mask):
    cur_mask = os.umask(new_mask)
    yield
    os.umask(cur_mask)


@contextmanager
def setenv(env):
    """os.environ context manager. Updates os.environ with the specified
    `env` for the duration of the context.

    """
    old_env = {}
    for key in env:
        old_env[key] = os.environ.get(key)
        os.environ[key] = env[key]

    yield

    for key in old_env:
        if old_env[key] is None:
            del os.environ[key]
        else:
            os.environ[key] = old_env[key]


class Builder:
    """Builder manages the build process.

    A builder is created for a specific build/host/target combination
    and holds state common to building any specific package.

    The primary entry points for users of the is the `build` method,
    which is used to build a named package.

    Additionally the Builder object is passed to the per-package rules
    methods, and provides a group of useful methods that can be re-used
    by multiple different packages.

    FIXME: The methods used by rules methods generally don't actually
    use the `self` argument so may be better structured as module scope
    functions or class methods.

    """

    def __init__(self, build=None, host=None, target=None, jobs=1):
        detected_build = self._detect_build()
        if build is None:
            build = detected_build
            logger.info("Detected build: {}".format(build))
        if host is None:
            host = build

        if build != detected_build:
            logger.warning("Provided build {} does not match detected build {}.".format(
                    build, detected_build))

        self.rules_dir = os.path.join(os.path.dirname(__file__), 'rules')
        self.build_platform = build
        self.host = host
        self.target = target
        self.packaging_dir = ''
        self.source_path = os.path.join(self.packaging_dir, 'source')
        self.build_path = os.path.join(self.packaging_dir, 'build')
        self.jobs = jobs
        ensure_dir(self.source_path)

    def _detect_build(self):
        """Return the platform triple for the current host based on what
        can be determined from introspection.

        """
        build = None
        plat = sys.platform
        arch = platform.architecture()[0]

        if plat == 'darwin' and arch == '64bit':
            build = 'x86_64-apple-darwin'
        elif plat == 'linux2' and arch == '64bit':
            build = 'x86_64-unknown-linux-gnu'
        # Add other supported platforms as required.

        if build is None:
            raise Exception("Unsupported platform/architecture: {}/{}".format(plat, arch))
        return build

    def build(self, pkg_name, reconfigure=False):
        """Build a specified package.

        By default the build process avoid re-running the configuration process,
        however this can be forced by setting `reconfigure` to true.

        """
        rules = self._load_rules(pkg_name)
        # Check
        rules.check(self)
        # Prepare
        config = self._std_config(pkg_name)
        config = rules.prepare(self, config)

        # Install all deps
        # Install all deps
        for dep in rules.deps:
            ensure_dir(config['devtree_dir'])
            qual_format = '{dep}-{target}-{host}'
            qualifed_dep = qual_format.format(dep=dep, **config)
            rel_file = '{release_dir}/{dep}.tar.bz2'.format(dep=qualifed_dep, **config)
            if not os.path.exists(rel_file):
                qual_format = '{dep}-{host}'
                qualifed_dep = qual_format.format(dep=dep, **config)
                rel_file = '{release_dir}/{dep}.tar.bz2'.format(dep=qualifed_dep, **config)

            logger.info("Installing dep: %s", qualifed_dep)
            self.cmd('tar', 'xf', rel_file, '-C', '{devtree_dir}', config=config)


        # Download
        self._download(config)
        # Configure
        self._configure(rules, config, reconfigure)
        # Make
        with chdir(config['build_dir']):
            rules.make(self, config)
        # Install
        if os.path.exists(config['install_dir']):
            shutil.rmtree(config['install_dir'])
        ensure_dir(config['install_dir'])
        rules.install(self, config)
        # Package
        self._package(config)

    def _load_rules(self, pkg_name):
        """Load and return the rules for a named packaged."""
        module_name = 'rules.{}'.format(pkg_name)
        __import__(module_name)
        pkg_rules = sys.modules[module_name].rules
        assert pkg_rules.pkg_name == pkg_name
        return pkg_rules

    def _std_config(self, pkg_name):
        """Generate the standard configuration for a given package.

        Config returns a dictionary with a set of standard key-value
        pairs which are used by package rules during the build process.

        The standard configuration keys are:

        pkg_name: Name of the package.
        qualified_pkg_name: The name of the packaged qualified by the
          host and target platform names.
        target: Target platform (passed as --target to configure).
        host: Host platform (passed as --host to configure).
        build: Build platform (passed as --build to configure).

        prefix: Default install location (passed as --prefix to configure).
        eprefix: Executable install location (passed as --eprefix to configure).

        root_dir: The root directory for package build process.
        source_dir: Location of package source.
        source_dir_from_build: Location of package source while in the build directory.
        build_dir: Location of the build directory. This is where e.g.: configure and
          make are run.
        install_dir: Location of the install directory.
        install_dir_abs: Absolute path to the install_dir. (Absolute paths are usually
          required by `make install`.)
        release_dir: Packages ready for release are stored in the release directory.
        release_file: The released package's filename.
        repo_name: Repository name.
        jobs: Specifies number of concurrent jobs to run, in the form -jN. Designed
          to be passed directly to make.
        standard_ldflags: Standard linker flags, generally used to set LDFLAGS environment
          variable.
        """
        config = {}

        config['pkg_name'] = pkg_name

        config['target'] = self.target
        config['host'] = self.host
        config['build'] = self.build_platform

        if config['target'] is not None:
            qual_format = '{pkg_name}-{target}-{host}'
        else:
            qual_format = '{pkg_name}-{host}'
        config['qualifed_pkg_name'] = qual_format.format(**config)

        config['prefix'] = '/noprefix'
        config['eprefix'] = self.j('{prefix}', '{host}', config=config)

        config['root_dir'] = self.packaging_dir
        config['source_dir'] = self.j('{root_dir}', 'source', '{pkg_name}', config=config)
        if os.path.isabs(config['root_dir']):
            config['source_dir_from_build'] = config['source_dir']
        else:
            # FIXME: This works when the default build_dir is in place, but
            # may not in other circumstances
            config['source_dir_from_build'] = self.j('..', '..', '{source_dir}', config=config)

        config['build_dir'] = self.j('{root_dir}', 'build', '{qualifed_pkg_name}', config=config)
        config['devtree_dir'] = self.j('{root_dir}', 'devtree', '{qualifed_pkg_name}', config=config)
        config['devtree_dir_abs'] = os.path.abspath(config['devtree_dir'])
        config['install_dir'] = self.j('{root_dir}', 'install', '{qualifed_pkg_name}', config=config)
        config['install_dir_abs'] = os.path.abspath(config['install_dir'])

        config['release_dir'] = self.j('{root_dir}', 'release', config=config)
        config['release_file'] = self.j('{release_dir}', '{qualifed_pkg_name}.tar.bz2', config=config)

        config['repo_name'] = SOURCE_REPO_PREFIX + pkg_name

        if config['build'].endswith('-darwin'):
            config['standard_ldflags'] = "-Wl,-Z -Wl,-search_paths_first"
        elif config['build'].endswith('-linux-gnu'):
            config['standard_ldflags'] = ""
        else:
            raise UsageError("Can't determine LD flags for {build}".format(**config))

        config['standard_ldflags'] += " -L{devtree_dir_abs}/{host}/lib".format(**config)
        config['standard_cppflags'] = "-I{devtree_dir_abs}/include -I{devtree_dir_abs}/{host}/include".format(**config)

        config['jobs'] = "-j{}".format(self.jobs)

        return config

    def _download(self, config, force=False):
        """Download the package source from git.

        If the source already exists the downloading is skipped, unles
        the force argument is set to True, in which case the existing
        source directory is removed before re-downloading the source.

        """
        if force and os.path.exists(config['source_dir']):
            shutil.rmtree(config['source_dir'])
        if not os.path.exists(config['source_dir']):
            cmd = 'git clone {repo_name} {source_dir}'.format(**config)
            logger.info(cmd)
            os.system(cmd)

        # FIXME: Additional work required here to ensure the correct version
        # is currently checked out in the source directory.

    def _configure(self, rules, config, reconfigure):
        configured_flag = self.j('{build_dir}', '.configured', config=config)
        if os.path.exists(configured_flag):
            if reconfigure:
                logger.info("{pkg_name} already configured. Reconfiguring.".format(**config))
                os.unlink(configured_flag)
            else:
                logger.info("{pkg_name} already configured. Aborting".format(**config))
                return
        ensure_dir(config['build_dir'])

        with chdir(config['build_dir']):
            rules.configure(self, config)

        touch(configured_flag)

    def _package(self, config):
        ensure_dir(config['release_dir'])
        pkg_root = self.j('{install_dir}', config['prefix'][1:], config=config)
        tar_bz2('{release_file}'.format(**config), pkg_root)

    def j(self, *args, config={}):
        return os.path.join(*[a.format(**config) for a in args])

    def cmd(self, cmd, *args, env={}, config={}):
        _env = {'PATH': '{devtree_dir_abs}/{host}/bin:/usr/bin:/bin'.format(**config)}
        _env.update(env)
        for key in _env:
            _env[key] = _env[key].format(**config)

        args = [cmd] + list(args)
        args = [a.format(**config) for a in args]
        cmd = ' '.join(args)  # FIXME: Not 100% accurate
        logger.info('{} ENV={}\n'.format(cmd, _env))

        with setenv(_env):
            r = os.system(cmd)
            if r != 0:
                raise Exception("Error: {}".format(r))

    def host_lib_configure(self, *extra_args, env={}, config={}):
        args = ('{source_dir_from_build}/configure',
                 '--prefix={prefix}',
                 '--exec-prefix={eprefix}',
                 '--host={host}',
                 '--build={build}',
                 '--disable-shared',
                 )
        base_env = {'LDFLAGS': '{standard_ldflags}',
                    'CPPFLAGS': '{standard_cppflags}',
                    }
        base_env.update(env)
        self.cmd(*(args + extra_args), env=base_env, config=config)

    def cross_configure(self, *extra_args, env={}, config={}):
        args = ('{source_dir_from_build}/configure',
                '--prefix={prefix}',
                '--exec-prefix={eprefix}',
                '--program-prefix={target}-',
                '--host={host}',
                '--build={build}',
                '--target={target}')
        base_env = {'LDFLAGS': '{standard_ldflags}'}
        base_env.update(env)
        self.cmd(*(args + extra_args), env=base_env, config=config)

    def __str__(self):
        return '<Builder: build={} host={} target={}>'.format(self.build, self.host, self.target)


class BuildProtocol:
    """Base class for rules implementations.

    The rules sub-class is expected to at least provide an
    implementation of configure.

    The sub-class should set the class variable `pkg_name`.

    FIXME: Maybe it is clearer if all these methods are class
    methods, rather than instance methods.

    """
    pkg_name = None
    deps = []

    def check(self, builder):
        """check can perform various checks to ensure that the package
        can be built in the current environment. check should raise
        a UserError exception in the case where the package can not
        be built.

        """
        pass

    def prepare(self, builder, config):
        """prepare returns a configuration dictionary containing the appropriate
        set of key-value pairs needed for the configure/make/install/package
        build phases.

        The prepare method is passed a standard set of config values by the builder.
        Usually the
        """
        return config

    def configure(self, builder):
        """configure should (logically) configure the build directory ready for making.
        Generally it is expected that this involves running a `configure` script or the
        equivalent.

        """
        raise Exception()

    def make(self, builder, config):
        """make invokes the make utility in the build directory."""
        builder.cmd('make', '{jobs}', config=config)

    def install(self, builder, config):
        """install places the built files in to the install
        dir. Whatever is in the install directory at the completion of
        this command is packaged by the builder for release.

        """
        with chdir(config['build_dir']), umask(0o22):
            builder.cmd('make', 'DESTDIR={install_dir_abs}', 'install', config=config)

        # Now remove the silly info/dir file if it exists.
        info_dir = builder.j('{install_dir}', config['prefix'][1:], 'share', 'info', 'dir', config=config)
        if os.path.exists(info_dir):
            os.unlink(info_dir)

        # And remove any .la files
        for root, _, files in os.walk('{install_dir}'.format(**config)):
            for f in files:
                if f.endswith('.la'):
                    os.unlink(os.path.join(root, f))

        # Remove the header from man page
        with umask(0o22):
            man_dir = builder.j('{install_dir}', config['prefix'][1:], 'share', 'man', config=config)
            for root, _, files in os.walk(man_dir):
                for f in files:
                    man_remove_header(os.path.join(root, f))


    def __str__(self):
        return "<{}>".format(self.__class__.__name__)


def check_releases():
    release_dir = 'release'
    all_files = {}
    for f in os.listdir(release_dir):
        print(f)
        with tarfile.open(os.path.join(release_dir, f)) as t:
            for m in t.getmembers():
                if m.type not in (tarfile.REGTYPE, tarfile.DIRTYPE, tarfile.LNKTYPE, tarfile.SYMTYPE):
                    raise Exception("{} is the wrong type ({})".format(m.name, m.type))

                e_type = {tarfile.REGTYPE: 'FILE', tarfile.DIRTYPE: 'DIR', tarfile.LNKTYPE: 'LINK', tarfile.SYMTYPE: 'SYMLINK'}[m.type]
                extra = ''
                if m.islnk():
                    extra = '==> ' + m.linkname
                    d = m.linkname
                elif m.issym():
                    extra = '--> ' + m.linkname
                    d = m.linkname
                elif m.isfile():
                    data = t.extractfile(m.name).read()
                    digest = hashlib.sha256(data).hexdigest()
                    d = digest
                    extra = digest
                elif m.isdir():
                    d = None

                dupe = ' '
                info_pack = (e_type, d, m.mtime, m.mode, m.uid, m.gid, m.uname, m.gname)
                if m.name in all_files:
                    dupe = 'X'
                    if all_files[m.name] != info_pack:
                        print("{} already extracted! {} != {}".format(m.name, all_files[m.name], info_pack))
                    #assert all_files[m.name] == (e_type, d)
                all_files[m.name] = info_pack
                print('\t{} - {:10s} {} {}'.format(dupe, e_type, m.name, extra))


def main(args):
    """main entry point. args is a list of arguments, generally provided directly
    from sys.argv

    main returns a integer value generally suitable for passing to `sys.exit`.

    """
    import argparse

    parser = argparse.ArgumentParser(description='XYZ package builder.')
    parser.add_argument('--build', help='Explicitly set the build system. (default: autodetect)')
    parser.add_argument('--host', help='Explicitly set the host system. (default: build)')
    parser.add_argument('--target', help='Explicitly set the target system (for toolchains). (default: None)')
    parser.add_argument('--reconfigure', help='Reconfigure. (default: False)', action='store_true', default=False)
    parser.add_argument('-j', dest='jobs', help='Simultaneous jobs. (default: 1)', type=int, default=1)
    parser.add_argument('--check-releases', dest='check_releases', action='store_true', default=False,
                        help='Check that the release files are consistent.')
    parser.add_argument('packages', metavar='PKG', nargs='*', help='list of packages to build')

    args = parser.parse_args(args[1:])

    if (args.check_releases and len(args.packages) > 0):
        parser.error("Do not specify packages when checking releases.")
    elif (not args.check_releases and len(args.packages) == 0):
        parser.error("At least one package must be listed.")

    if args.check_releases:
        check_releases()
        return 0

    b = Builder(args.build, args.host, args.target, args.jobs)
    for pkg in args.packages:
        b.build(pkg, args.reconfigure)

    return 0


if __name__ == '__main__':
    # Standard run-module as script stuff.
    import sys
    try:
        sys.exit(main(sys.argv))
    except UsageError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        # If the user Ctrl-Cs we ignore it
        pass
