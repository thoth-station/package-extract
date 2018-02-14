#!/usr/bin/env python3
"""Command line interface for thoth-pkgdeps."""

import datetime
import json
import logging
import platform
import sys
import typing

import click
import requests

import daiquiri
from thoth_pkgdeps import __version__ as thothg_pkgdeps_version
from thoth_pkgdeps.core import extract_buildlog
from thoth_pkgdeps.core import extract_image

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

    click.echo("{!s}".format(thothg_pkgdeps_version))
    ctx.exit()


def _print_command_result(result: typing.Union[dict, list], output: str = None,
                          pretty: bool = True, metadata: dict = None) -> None:
    """Print or submit results, nicely if requested."""
    metadata = metadata or {}
    metadata['version'] = thothg_pkgdeps_version
    metadata['datetime'] = datetime.datetime.now().isoformat()
    metadata['hostname'] = platform.node()
    metadata['analyzer'] = __name__.split('.')[0]

    content = {
        'result': result,
        'metadata': metadata
    }

    if isinstance(output, str) and output.startswith(('http://', 'https://')):
        _LOG.info("Submitting results to %r", output)
        response = requests.post(output, json=content)
        response.raise_for_status()
        _LOG.info("Successfully submitted results to remote, response: %s", response.json())
        return

    kwargs = {}
    if pretty:
        kwargs['sort_keys'] = True
        kwargs['separators'] = (',', ': ')
        kwargs['indent'] = 2

    content = json.dumps(content, **kwargs)
    if output is None or output == '-':
        sys.stdout.write(content)
    else:
        _LOG.info("Writing results to %r", output)
        with open(output, 'w') as output_file:
            output_file.write(content)


@click.group()
@click.pass_context
@click.option('-v', '--verbose', is_flag=True, envvar='THOTH_ANALYZER_DEBUG',
              help="Be verbose about what's going on.")
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
@click.option('--output', '-o', type=str, envvar='THOTH_ANALYZER_OUTPUT', default=None,
              help="Output file or remote API to print results to, in case of URL a POST request is issued.")
def cli_extract_buildlog(input_file, no_pretty=False, output=None):
    """Extract installed packages from a build log."""
    result = extract_buildlog(input_file.read())
    _print_command_result(result, output, not no_pretty, metadata={'output': output})


@cli.command('extract-image')
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
def cli_extract_image(image, timeout=None, no_pretty=False, output=None):
    """Extract installed packages from an image."""
    arguments = locals()
    result = extract_image(image, timeout)
    _print_command_result(result, output, not no_pretty, metadata={'arguments': arguments})


if __name__ == '__main__':
    sys.exit(cli())
