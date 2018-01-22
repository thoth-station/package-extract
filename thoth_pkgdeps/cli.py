#!/usr/bin/env python3
"""Command line interface for thoth-pkgdeps."""

import json
import logging
import sys
import typing

import click

import daiquiri
from thoth_pkgdeps import __version__ as thothg_pkgdeps_version
from thoth_pkgdeps.core import extract_buildlog
from thoth_pkgdeps.core import extract_image

_LOG = logging.getLogger(__name__)
_DEFAULT_NO_COLOR_FORMAT = "%(asctime)s [%(process)d] %(levelname)-8.8s %(name)s: %(message)s"
_DEFAULT_COLOR_FORMAT = "%(asctime)s [%(process)d] %(color)s%(levelname)-8.8s %(name)s: %(message)s%(color_stop)s"


def _setup_logging(verbose: int, no_color: bool) -> None:
    """Set up logging facilities.

    :param verbose: verbosity level
    :param no_color: do not use color in output
    """
    level = logging.WARNING
    if verbose == 1:
        level = logging.INFO
    elif verbose > 1:
        level = logging.DEBUG

    formatter = daiquiri.formatter.ColorFormatter(fmt=_DEFAULT_COLOR_FORMAT)
    if no_color:
        formatter = logging.Formatter(fmt=_DEFAULT_NO_COLOR_FORMAT)

    daiquiri.setup(level=level, outputs=(
        daiquiri.output.Stream(formatter=formatter),
    ))


def _print_version(ctx, _, value):
    """Print version information and exit."""
    if not value or ctx.resilient_parsing:
        return

    click.echo("{!s}".format(thothg_pkgdeps_version))
    ctx.exit()


def _print_command_result(result: typing.Union[dict, list], pretty=True) -> None:
    """Print results, nicely if requested."""
    kwargs = {}
    if pretty:
        kwargs['sort_keys'] = True
        kwargs['separators'] = (',', ': ')
        kwargs['indent'] = 2

    click.echo("{!s}".format(json.dumps(result, **kwargs)))


@click.group()
@click.pass_context
@click.option('-v', '--verbose', count=True,
              help="Be verbose about what's going on (can be supplied multiple times).")
@click.option('--version', is_flag=True, is_eager=True, callback=_print_version, expose_value=False,
              help="Print thoth_pkgdeps version and exit.")
@click.option('--no-color', '-C', is_flag=True,
              help="Suppress colorized logging output.")
def cli(ctx=None, verbose: int = 0, no_color: bool = True):
    """Thoth pkgdeps command line interface."""
    if ctx:
        ctx.auto_envvar_prefix = 'THOTH_PKGDEPS'

    _setup_logging(verbose, no_color)


@cli.command('extract-buildlog')
@click.option('--input-file', '-i', type=click.File('r'), required=True,
              help="Input file - build logs to be checked.")
@click.option('--no-pretty', is_flag=True,
              help="Do not print results nicely.")
def cli_extract_buildlog(input_file, no_pretty=False):
    """Extract installed packages from a build log."""
    result = extract_buildlog(input_file.read())
    _print_command_result(result, not no_pretty)


@cli.command('extract-image')
@click.option('--image', '-i', type=str, required=True, envvar='THOTH_IMAGE',
              help="Image name from which packages should be extracted.")
@click.option('--no-pretty', is_flag=True,
              help="Do not print results nicely.")
@click.option('--timeout', '-t', type=int, required=False, default=None, show_default=True, envvar='THOTH_TIMEOUT',
              help="Soft timeout for extraction - timeout is set to commands run, the actual execution time of "
                   "this tool will be bigger.")
def cli_extract_image(image, timeout=None, no_pretty=False):
    """Extract installed packages from an image."""
    result = extract_image(image, timeout)
    _print_command_result(result, not no_pretty)


if __name__ == '__main__':
    sys.exit(cli())
