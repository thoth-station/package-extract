#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# thoth-package-extract
# Copyright(C) 2018 Fridolin Pokorny
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

"""Manipulation with an image and image scanning."""

import json
import logging
import os
import tarfile
import typing
from shlex import quote

from thoth.analyzer import run_command
from thoth.common import cwd

from .exceptions import InvalidImageError
from .exceptions import NotSupported
from .koji import KojiError
from .koji import parse_NVR
from .koji import parse_NVRA

_LOGGER = logging.getLogger(__name__)

_MERCATOR_BIN = os.getenv('MERCATOR_BIN', 'mercator')
_MERCATOR_HANDLERS_YAML = os.getenv('MERCATOR_HANDLERS_YAML', '/usr/share/mercator/handlers.yml')


def _normalize_mercator_output(path: str, output: dict) -> dict:
    """Normalize and filter mercator output."""
    output = output or {}
    for entry in output.get('items') or []:
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


def _run_rpm_repoquery(path: str, timeout: int = None) -> list:
    """Run repoquery and return it's output (parsed)."""
    cmd = 'repoquery --deplist --installed --installroot {!r}'.format(path)
    output = _parse_repoquery(run_command(cmd, timeout=timeout).stdout)

    result = []
    for package_identifier, dependencies in output.items():
        try:
            rpm_package = parse_NVRA(package_identifier)
        except KojiError:
            rpm_package = parse_NVR(package_identifier)
            # Fill in missing parts missing in parse_NVR() output, but present in parse_NVRA().
            rpm_package['src'] = False
            rpm_package['arch'] = None

        rpm_package['dependencies'] = dependencies
        rpm_package['epoch'] = rpm_package['epoch'] or None
        rpm_package['package_identifier'] = package_identifier
        result.append(rpm_package)

    return result


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


def construct_rootfs(dir_path: str, rootfs_path: str) -> list:
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

    layers = []
    _LOGGER.debug("Layers found: %r", manifest['layers'])
    for layer_def in manifest['layers']:
        layer_digest = layer_def['digest'].split(':', maxsplit=1)[-1]

        _LOGGER.debug("Extracting layer %r", layer_digest)
        layers.append(layer_digest)

        layer_gzip_tar = os.path.join(dir_path, layer_digest)
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

    return layers


def download_image(image_name: str, dir_path: str, timeout: int = None, registry_credentials: str = None,
                   tls_verify: bool = True) -> None:
    """Download an image to dir_path."""
    _LOGGER.debug("Downloading image %r", image_name)

    cmd = 'skopeo copy '
    if not tls_verify:
        cmd += '--src-tls-verify=false '
    if registry_credentials:
        cmd += '--src-creds={} '.format(quote(registry_credentials))

    cmd += 'docker://{} dir:/{}'.format(quote(image_name), quote(dir_path))
    stdout = run_command(cmd, timeout=timeout).stdout
    _LOGGER.debug("skopeo stdout: %s", stdout)


def run_analyzers(path: str, timeout: int = None) -> dict:
    """Run analyzers on the given path (directory) and extract found packages."""
    path = quote(path)
    return {
        'mercator': _run_mercator(path, timeout=timeout),
        'rpm': _run_rpm(path, timeout=timeout),
        'rpm-dependencies': _run_rpm_repoquery(path, timeout=timeout)
    }
