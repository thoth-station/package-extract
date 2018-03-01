"""Manipulation with an image and image scanning."""

import json
import logging
import os
import tarfile
import typing

from thoth.analyzer import run_command
from thoth.common import cwd

from .exceptions import InvalidImageError
from .exceptions import NotSupported

_LOGGER = logging.getLogger(__name__)

_MERCATOR_BIN = os.getenv('MERCATOR_BIN', 'mercator')
_MERCATOR_HANDLERS_YAML = os.getenv('MERCATOR_HANDLERS_YAML', '/usr/share/mercator/handlers.yml')


def _normalize_mercator_output(path: str, output: dict) -> dict:
    """Normalize and filter mercator output."""
    for entry in output.get('items', []):
        entry.pop('time', None)

        # Now point to the correct path, absolute inside the image.
        if 'path' in entry:
            entry['path'] = entry['path'][len(path):]

    return output.get('items', [])


def _parse_repoquery(output: str) -> dict:
    """Parse repoquery output."""
    result = {}

    package = None
    for line in output.split('\n'):
        line = line.strip()

        if not line:
            continue

        if line.startswith('package: '):
            package = line[len('package: '):]
            if package in result:
                _LOGGER.warning("Package {!r} was already stated in the repoquery output, "
                                "dependencies will be appended")
                continue
            result[package] = []
        elif line.startswith('dependency: '):
            if not package:
                _LOGGER.error("Stated dependency %r has no package associated (parser error?), this error is not fatal")
            result[package].append(line[len('dependency: '):])

    return result


def _run_rpm_repoquery(path: str, timeout: int = None):
    """Run repoquery and return it's output (parsed)."""
    cmd = 'repoquery --deplist --installed --installroot {!r}'.format(path)
    output = run_command(cmd, timeout=timeout).stdout
    return _parse_repoquery(output)


def _run_mercator(path: str, timeout: int = None) -> dict:
    """Run mercator-go to find all packages that were installed inside an image."""
    cmd = '{mercator_bin} -config {mercator_handlers_yaml} {path}'.format(
        mercator_bin=_MERCATOR_BIN,
        mercator_handlers_yaml=_MERCATOR_HANDLERS_YAML,
        path=path
    )
    output = run_command(cmd, env={'MERCATOR_INTERPRET_SETUP_PY': 'true'}, timeout=timeout, is_json=True).stdout
    return _normalize_mercator_output(path, output)


def _run_rpm(path: str, timeout: int = None) -> typing.List[str]:
    """Query for installed rpm packages in the given root described by path."""
    cmd = 'rpm -qa --root {!r}'.format(path)
    output = run_command(cmd, timeout=timeout).stdout
    packages = output.split('\n')
    if not packages[-1]:
        packages.pop()
    return packages


def construct_rootfs(dir_path: str, rootfs_path: str) -> None:
    """Construct rootfs in a directory by extracting layers."""
    os.makedirs(rootfs_path, exist_ok=True)

    try:
        with open(os.path.join(dir_path, 'manifest.json')) as manifest_file:
            manifest = json.load(manifest_file)
    except FileNotFoundError as exc:
        raise InvalidImageError("No manifest.json file found in the downloaded "
                                "image in {}".format(os.path.join(dir_path, 'manifest.json'))) from exc

    if manifest.get('schemaVersion') != 2:
        raise NotSupported("Invalid schema version in manifest.json file: {} "
                           "(currently supported is 2)".format(manifest.get('schemaVersion')))

    for layer_def in manifest['layers']:
        layer_digest = layer_def['digest'].split(':', maxsplit=1)[-1]
        _LOGGER.debug("Extracting layer %r", layer_digest)

        layer_gzip_tar = os.path.join(dir_path, "{}.tar".format(layer_digest))
        with cwd(rootfs_path):
            tar_file = tarfile.open(layer_gzip_tar, 'r:gz')

            # We cannot use extractall() since it does not handle overwriting files for us.
            for member in tar_file:
                # Do not set attributes so we are fine with permissions.
                try:
                    tar_file.extract(member, set_attrs=False)
                except IOError:
                    # If the given file is present, there is raised an exception - remove file to prevent from errors.
                    os.remove(member.name)
                    tar_file.extract(member, set_attrs=False)


def download_image(image_name: str, dir_path: str, timeout: int = None) -> None:
    """Download an image to dir_path."""
    _LOGGER.debug("Downloading image %s", image_name)
    cmd = 'skopeo copy docker://{image_name} dir:/{dir}'.format(image_name=image_name, dir=dir_path)
    stdout = run_command(cmd, timeout=timeout).stdout
    _LOGGER.debug("skopeo stdout: %s", stdout)


def run_analyzers(path: str, timeout: int = None) -> dict:
    """Run analyzers on the given path (directory) and extract found packages."""
    return {
        'mercator': _run_mercator(path, timeout=timeout),
        'rpm': _run_rpm(path, timeout=timeout),
        'rpm-dependencies': _run_rpm_repoquery(path, timeout=timeout)
    }
