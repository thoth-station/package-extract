#!/usr/bin/env python3
"""Command line interface for thoth-package-extract."""

import logging
import sys

import click

import daiquiri
from thoth.analyzer import print_command_result
from thoth.package_extract import __title__ as analyzer
from thoth.package_extract import __version__ as analyzer_version
from thoth.package_extract.core import extract_buildlog
from thoth.package_extract.core import extract_image

_LOG = logging.getLogger(__name__)
_DEFAULT_NO_COLOR_FORMAT = "%(asctime)s [%(process)d] %(levelname)-8.8s %(name)s: %(message)s"
_DEFAULT_COLOR_FORMAT = "%(asctime)s [%(process)d] %(color)s%(levelname)-8.8s %(name)s: %(message)s%(color_stop)s"


def _setup_logging(verbose: bool, no_color: bool) -> None:
    """Set up logging facilities.

    :param verbose: be verbose
    :param no_color: do not use color in output
    """
    level = logging.DEBUG if verbose else logging.INFO
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

    click.echo("{!s}".format(analyzer_version))
    ctx.exit()


@click.group()
@click.pass_context
@click.option('-v', '--verbose', is_flag=True, envvar='THOTH_ANALYZER_DEBUG',
              help="Be verbose about what's going on.")
@click.option('--version', is_flag=True, is_eager=True, callback=_print_version, expose_value=False,
              help="Print thoth-package-extract version and exit.")
@click.option('--no-color', '-C', is_flag=True,
              help="Suppress colorized logging output.")
def cli(ctx=None, verbose: bool = False, no_color: bool = True):
    """Thoth pkgdeps command line interface."""
    if ctx:
        ctx.auto_envvar_prefix = 'THOTH_PKGDEPS'

    _setup_logging(verbose, no_color)


@cli.command('extract-buildlog')
@click.pass_context
@click.option('--input-file', '-i', type=click.File('r'), required=True,
              help="Input file - build logs to be checked.")
@click.option('--no-pretty', is_flag=True,
              help="Do not print results nicely.")
@click.option('--output', '-o', type=str, envvar='THOTH_ANALYZER_OUTPUT', default=None,
              help="Output file or remote API to print results to, in case of URL a POST request is issued.")
def cli_extract_buildlog(click_ctx, input_file, no_pretty=False, output=None):
    """Extract installed packages from a build log."""
    result = extract_buildlog(input_file.read())
    print_command_result(click_ctx, result, analyzer=analyzer, analyzer_version=analyzer_version,
                         output=output or '-', pretty=not no_pretty)


@cli.command('extract-image')
@click.pass_context
@click.option('--image', '-i', type=str, required=True, envvar='THOTH_ANALYZED_IMAGE',
              help="Image name from which packages should be extracted.")
@click.option('--no-pretty', is_flag=True,
              help="Do not print results nicely.")
@click.option('--timeout', '-t', type=int, required=False, default=None, show_default=True,
              envvar='THOTH_ANALYZER_TIMEOUT',
              help="Soft timeout for extraction - timeout is set to commands run, the actual execution time of "
                   "this tool will be bigger.")
@click.option('--output', '-o', type=str, envvar='THOTH_ANALYZER_OUTPUT', default=None,
              help="Output file or remote API to print results to, in case of URL a POST request is issued.")
def cli_extract_image(click_ctx, image, timeout=None, no_pretty=False, output=None):
    """Extract installed packages from an image."""
    result = extract_image(image, timeout)
    print_command_result(click_ctx, result, analyzer=analyzer, analyzer_version=analyzer_version,
                         output=output or '-', pretty=not no_pretty)


if __name__ == '__main__':
    sys.exit(cli())
