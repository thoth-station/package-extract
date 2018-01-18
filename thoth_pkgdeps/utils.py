"""Various utilities for thoth-pkgdeps tools."""

from contextlib import contextmanager
import logging
import os
import shlex
import shutil
import subprocess
import tempfile

from .exceptions import TimeoutExpired

_LOGGER = logging.getLogger(__name__)


def run_command(cmd: str, timeout: int = None, env: dict = None) -> str:
    """Run the given command and return its stdout.

    :param cmd: a string containing a command that should be run
    :type cmd: str
    :param env: additional environment variables that should be supplied
    :type env: dict
    :param timeout: timeout for command to be used
    :type timeout: int
    :type: str
    :return: stdout produced by the command
    :raises RuntimeError: signalizing process exited with non-zero value
    :raises TimeoutExpired: signalizing process timeout after the given time
    """
    _LOGGER.debug("Running command %r%s", cmd,
                  " with timeout {} and environment {}".format(timeout, (env if env else "unchanged")))
    args = shlex.split(cmd)
    environment = dict(os.environ).update(**(env or {}))

    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        env=environment
    )

    try:
        output, errs = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise TimeoutExpired("Running command {!r} timed out after {!s} seconds".format(cmd, timeout)) from exc

    if errs:
        _LOGGER.warning("%s: %s", args[0], errs)

    if process.returncode != 0:
        raise RuntimeError("Command %s exited with non-zero exit value (called as: %r)" % (args[0], args))

    return str(output)


@contextmanager
def cwd(target_dir: str) -> str:
    """Change working directory in pushd-popd fashion with context manger."""
    current_directory = os.getcwd()
    os.chdir(target_dir)
    try:
        yield current_directory
    finally:
        os.chdir(current_directory)


@contextmanager
def tempdir() -> str:
    """Create a temporary directory and temporary cd into it with context manager."""
    dir_path = tempfile.mkdtemp()

    try:
        with cwd(dir_path):
            yield dir_path
    finally:
        if os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
