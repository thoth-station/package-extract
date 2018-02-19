"""Manipulation with an image and image scanning."""

import json
import logging
import os
import tarfile
import typing

from .exceptions import InvalidImageError
from .exceptions import NotSupported
from .utils import cwd
from .utils import run_command

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
    output = run_command(cmd, timeout=timeout)
    return _parse_repoquery(output)


def _run_mercator(path: str, timeout: int = None) -> dict:
    """Run mercator-go to find all packages that were installed inside an image."""
    cmd = '{mercator_bin} -config {mercator_handlers_yaml} {path}'.format(
        mercator_bin=_MERCATOR_BIN,
        mercator_handlers_yaml=_MERCATOR_HANDLERS_YAML,
        path=path
    )
    output = run_command(cmd, env={'MERCATOR_INTERPRET_SETUP_PY': 'true'}, timeout=timeout)
    return _normalize_mercator_output(path, json.loads(output))


def _run_rpm(path: str, timeout: int = None) -> typing.List[str]:
    """Query for installed rpm packages in the given root described by path."""
    cmd = 'rpm -qa --root {!r}'.format(path)
    output = run_command(cmd, timeout=timeout)
    packages = output.split('\n')
    if not packages[-1]:
        packages.pop()
    return packages


def construct_rootfs(dir_path: str, rootfs_path: str) -> typing.Generator[str, None, None]:
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

    for layer_idx, layer_def in enumerate(manifest['layers']):
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

        yield layer_digest


def _analyzers_update_output(old_output: dict, layer: str,
                             mercator_output: list, rpm_output: dict, rpm_repoquery_output: dict) -> dict:
    old_output['mercator'] = old_output.get('mercator', [])
    mercator_seen_packages = set()
    for entry in old_output['mercator']:
        mercator_seen_packages.add((entry['result'].get('name'), entry['result'].get('version'),
                                    entry['digests']['manifest']))

    for entry in mercator_output:
        record = (entry['result']['name'], entry['result']['version'], entry['digests']['manifest'])
        if record not in mercator_seen_packages:
            entry['layer'] = layer
            old_output['mercator'].append(entry)

    old_output['rpm'] = old_output.get('rpm', [])
    rpm_seen_packages = {entry['name'] for entry in old_output['rpm']}
    for package in set(rpm_output) - rpm_seen_packages:
        old_output['rpm'].append({
            'name': package,
            'layer': layer
        })

    old_output['rpm-dependencies'] = list(set(rpm_repoquery_output) | set(old_output.get('rpm-dependencies', set())))

    old_output['layers'] = old_output.get('layers', [])
    old_output['layers'].append(layer)
    return old_output


def download_image(image_name: str, dir_path: str, timeout: int = None) -> None:
    """Download an image to dir_path."""
    _LOGGER.debug("Downloading image %s", image_name)
    cmd = 'skopeo copy docker://{image_name} dir:/{dir}'.format(image_name=image_name, dir=dir_path)
    stdout = run_command(cmd, timeout=timeout)
    _LOGGER.debug("skopeo stdout: %s", stdout)


def run_analyzers(path: str, old_output: dict = None, layer: str = None, timeout: int = None) -> dict:
    """Run analyzers on the given path (directory) and extract found packages."""
    old_output = old_output or {}

    return _analyzers_update_output(
        old_output,
        layer,
        mercator_output=_run_mercator(path, timeout=timeout),
        rpm_output=_run_rpm(path, timeout=timeout),
        rpm_repoquery_output=_run_rpm_repoquery(path, timeout=timeout)
    )
