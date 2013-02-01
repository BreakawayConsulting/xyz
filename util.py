import contextlib
import hashlib
import os
import shutil
import subprocess
from functools import wraps


def sha256_file(filename):
    with open(filename, "rb") as f:
        data = f.read()
        return hashlib.sha256(data).hexdigest()


def rmtree(path):
    # FIXME: This has time-of-check time-of-use problem.
    # should really catch the right exception instead.
    if os.path.exists(path):
        logger.info("Removing tree '{}'".format(path))
        shutil.rmtree(path)

class _GeneratorSimpleContextManager(contextlib._GeneratorContextManager):
    """Helper for @simplecontextmanager decorator."""

    def __exit__(self, type, value, traceback):
        if type is None:
            try:
                next(self.gen)
            except StopIteration:
                return
            else:
                raise RuntimeError("generator didn't stop")
        else:
            if value is None:
                # Need to force instantiation so we can reliably
                # tell if we get the same exception back
                value = type()

            try:
                next(self.gen)
            except StopIteration as exc:
                # Suppress the exception *unless* it's the same exception that
                # was passed to throw().  This prevents a StopIteration
                # raised inside the "with" statement from being suppressed
                return exc is not value
            else:
                raise RuntimeError("generator didn't stop")
            finally:
                return False


def simplecontextmanager(func):
    """@simplecontextmanager decorator.

    Typical usage:

        @simplecontextmanager
        def some_generator(<arguments>):
            <setup>
            yield <value>
            <cleanup>

    This makes this:

        with some_generator(<arguments>) as <variable>:
            <body>

    equivalent to this:

        <setup>
        try:
            <variable> = <value>
            <body>
        finally:
            <cleanup>

    """
    @wraps(func)
    def helper(*args, **kwds):
        return _GeneratorSimpleContextManager(func, *args, **kwds)
    return helper


def ensure_dir(path):
    """Ensure that a specific directory exists."""
    return os.makedirs(path, exist_ok=True)


def touch(path):
    """Create an empty file (just like the unix touch command)."""
    open(path, 'w').close()


def file_list(root, full_path=False, sort=True):
    if not root.endswith('/'):
        root += '/'
    for base, dirs, files in os.walk(root):
        if sort:
            dirs.sort()
            files.sort()
        if not full_path:
            base = base[len(root):]
        for f in files:
            yield os.path.join(base, f)


def git_ver(path):
    with chdir(path):
        cmd = ['git', 'log', '-1', '--pretty=%H']
        source_ver = subprocess.check_output(cmd).decode().strip()
        cmd = ['git', 'status', '--porcelain']
        dirty = subprocess.check_output(cmd).decode().strip()
        if len(dirty) > 0:
            source_ver += '*'
        return source_ver

@simplecontextmanager
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


@simplecontextmanager
def umask(new_mask):
    cur_mask = os.umask(new_mask)
    yield
    os.umask(cur_mask)


@simplecontextmanager
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
