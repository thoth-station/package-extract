#!/usr/bin/env python3
# thoth-package-extract
# Copyright(C) 2018, 2019, 2020 Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Command line interface for thoth-package-extract."""

import logging
import sys
import time

import click

from thoth.common import init_logging
from thoth.common import __version__ as __common_version__
from thoth.analyzer import print_command_result
from thoth.analyzer import __version__ as __analyzer_version__
from thoth.package_extract import __title__ as analyzer
from thoth.package_extract import __version__ as analyzer_version
from thoth.package_extract.core import extract_image

__component_version__ = (
    f"{analyzer_version}+"
    f"common.{__common_version__}.analyzer.{__analyzer_version__}"
)

init_logging()
_LOG = logging.getLogger("thoth.package_extract")


def _print_version(ctx, _, value):
    """Print version information and exit."""
    if not value or ctx.resilient_parsing:
        return

    click.echo("{!s}".format(analyzer_version))
    ctx.exit()


@click.group()
@click.pass_context
@click.option("-v", "--verbose", is_flag=True, help="Be verbose about what's going on.")
@click.option(
    "--version",
    is_flag=True,
    is_eager=True,
    callback=_print_version,
    expose_value=False,
    help="Print thoth-package-extract version and exit.",
)
@click.option(
    "--metadata",
    type=str,
    envvar="THOTH_PACKAGE_EXTRACT_METADATA",
    help="Metadata in a form of a JSON which are used for carrying additional context in Thoth deployment.",
)
def cli(ctx=None, verbose: bool = False, metadata: str = None):
    """Thoth package-extract command line interface."""
    if ctx:
        ctx.auto_envvar_prefix = "THOTH_PACKAGE_EXTRACT"

    _LOG.setLevel(logging.DEBUG if verbose else logging.INFO)
    _LOG.debug("Debug mode is on")
    _LOG.info("Running thoth-package-extract in version %r", __component_version__)

    # This value is unused here, but is reported from click context.
    metadata = metadata


@cli.command("extract-image")
@click.pass_context
@click.option(
    "--image",
    "-i",
    type=str,
    required=True,
    envvar="THOTH_ANALYZED_IMAGE",
    help="Image name from which packages should be extracted.",
)
@click.option(
    "--registry-credentials",
    "-c",
    type=str,
    required=False,
    envvar="THOTH_REGISTRY_CREDENTIALS",
    metavar="USER:PASSWORD",
    help="Credentials to registry if needed. Token can be used as password.",
)
@click.option("--no-pretty", is_flag=True, help="Do not print results nicely.")
@click.option(
    "--timeout",
    "-t",
    type=int,
    required=False,
    default=None,
    show_default=True,
    envvar="THOTH_ANALYZER_TIMEOUT",
    help="Soft timeout for extraction - timeout is set to commands run, the actual execution time of "
    "this tool will be bigger.",
)
@click.option(
    "--output",
    "-o",
    type=str,
    envvar="THOTH_ANALYZER_OUTPUT",
    default=None,
    help="Output file or remote API to print results to, in case of URL a POST request is issued.",
)
@click.option(
    "--no-tls-verify",
    is_flag=True,
    envvar="THOTH_ANALYZER_NO_TLS_VERIFY",
    help="Do not verify TLS certificates of registry from which the image is pulled from.",
)
def cli_extract_image(
    click_ctx,
    image,
    timeout=None,
    no_pretty=False,
    output=None,
    registry_credentials=None,
    no_tls_verify=False,
):
    """Extract installed packages from an image."""
    start_time = time.monotonic()
    result = extract_image(
        image,
        timeout,
        registry_credentials=registry_credentials,
        tls_verify=not no_tls_verify,
    )
    print_command_result(
        click_ctx,
        result,
        analyzer=analyzer,
        analyzer_version=analyzer_version,
        output=output or "-",
        duration=time.monotonic() - start_time,
        pretty=not no_pretty,
    )


if __name__ == "__main__":
    sys.exit(cli())
