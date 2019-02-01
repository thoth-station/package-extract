#!/usr/bin/env python3
# thoth-package-extract
# Copyright(C) 2018, 2019 Fridolin Pokorny
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
import stat
from shlex import quote

from thoth.analyzer import run_command
from thoth.common import cwd

from .exceptions import InvalidImageError
from .exceptions import NotSupported
from .rpmlib import parse_nvra

_LOGGER = logging.getLogger(__name__)

_MERCATOR_BIN = os.getenv('MERCATOR_BIN', 'mercator')
_MERCATOR_HANDLERS_YAML = os.getenv('MERCATOR_HANDLERS_YAML', '/usr/local/share/mercator/handlers.yml')
_HERE_DIR = os.path.dirname(os.path.abspath(__file__))
_SKOPEO_EXEC_PATH = os.getenv('SKOPEO_EXEC_PATH', os.path.join(_HERE_DIR, 'bin', 'skopeo'))


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
        rpm_package = parse_nvra(package_identifier)

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


def _run_dpkg_query(path: str, timeout: int = None) -> typing.List[dict]:
    """Query for installed deb packages in the given root."""
    # Make sure dpkg-query exist, give up if not.
    dpkg_query_path = os.path.join(path, 'usr', 'bin', 'dpkg-query')
    if not os.path.isfile(dpkg_query_path):
        _LOGGER.info("Binary dpkg-query not found, deb packages discovery will not be performed")
        return []

    # Make sure dpkg-query is executable after extraction.
    st = os.stat(dpkg_query_path)
    os.chmod(dpkg_query_path, st.st_mode | stat.S_IEXEC)

    cmd = 'fakeroot fakechroot /usr/sbin/chroot {!r} /usr/bin/dpkg-query -l'.format(path)
    output = run_command(cmd, timeout=timeout).stdout
    result = []
    for line in output.split('\n'):
        if not line.startswith('ii '):
            _LOGGER.debug("Skipping line (not an installed package): %r", line)
            continue

        parts = line.split(maxsplit=4)
        if len(parts) < 4:
            _LOGGER.warning(
                "Line in dpkg-query output does not provide enough information to parse package name, "
                "version and architecture: %s", line
            )
            continue

        result.append({
            'name': parts[1],
            'version': parts[2],
            'arch': parts[3]
        })

    return result


def _parse_deb_dependency_line(line_str: str) -> typing.List[tuple]:
    """Parse deb dependency line respecting name of package and the given version range provided."""
    result = []
    for entry in line_str.split(', '):
        parts = entry.split(' (', maxsplit=1)
        if len(parts) == 2:
            result.append((parts[0], parts[1][:-1]))  # -1 to remove ending ')'
        else:
            # No version range specification defined.
            result.append((parts[0], None))
    return result


def _run_apt_cache_show(path: str, deb_packages: typing.List[dict], timeout: int = None) -> list:
    """Gather information about packages and their dependencies."""
    # Make sure dpkg-query exist, give up if not.
    if not deb_packages:
        return []

    apt_cache_path = os.path.join(path, 'usr', 'bin', 'apt-cache')
    if not os.path.isfile(apt_cache_path):
        _LOGGER.warning(
            "Binary apt-cache not found but debian packages were discovered previously - the output will not "
            "provide dependency information for debian packages"
        )
        return []

    # Make sure dpkg-query is executable after extraction.
    st = os.stat(apt_cache_path)
    os.chmod(apt_cache_path, st.st_mode | stat.S_IEXEC)

    result = []
    for record in deb_packages:
        cmd = 'fakeroot fakechroot /usr/sbin/chroot {!r} /usr/bin/apt-cache show {}={}'.format(
            path,
            record['name'],
            record['version']
        )

        # Do not touch original deb query, extend it rather with more info to follow rpm schema.
        entry = dict(record)
        parts = entry['version'].split(':', maxsplit=1)
        if len(parts) == 2:
            try:
                # If it parses int, its an epoch probably.
                int(parts[0])
                entry['epoch'] = parts[0]
                entry['version'] = parts[1]
            except ValueError:
                entry['epoch'] = None

        output = run_command(cmd, timeout=timeout).stdout
        entry['pre-depends'], entry['depends'], entry['replaces'] = [], [], []
        for line in output.splitlines():
            if line.startswith('Pre-Depends: '):
                deps = _parse_deb_dependency_line(line[len('Pre-Depends: '):])
                entry['pre-depends'] = [{'name': d[0], 'version': d[1]} for d in deps]
            elif line.startswith('Depends: '):
                deps = _parse_deb_dependency_line(line[len('Depends: '):])
                entry['depends'] = [{'name': d[0], 'version': d[1]} for d in deps]
            elif line.startswith('Replaces: '):
                deps = _parse_deb_dependency_line(line[len('Replaces: '):])
                entry['replaces'] = [{'name': d[0], 'version': d[1]} for d in deps]

        result.append(entry)

    return result


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
                    tar_file.extract(member, set_attrs=False, numeric_owner=False)
                except IOError:
                    # If the given file is present, there is raised an exception - remove file to prevent from errors.
                    try:
                        os.remove(member.name)
                        tar_file.extract(member, set_attrs=False, numeric_owner=False)
                    except Exception as exc:
                        _LOGGER.exception("Failed to extract %r, exception is not fatal: %s", member.name, exc)

    return layers


def download_image(image_name: str, dir_path: str, timeout: int = None, registry_credentials: str = None,
                   tls_verify: bool = True) -> None:
    """Download an image to dir_path."""
    _LOGGER.debug("Downloading image %r", image_name)

    cmd = f'{_SKOPEO_EXEC_PATH} copy '
    if not tls_verify:
        cmd += '--src-tls-verify=false '
    if registry_credentials:
        cmd += '--src-creds={} '.format(quote(registry_credentials))

    cmd += 'docker://{} dir:/{}'.format(quote(image_name), quote(dir_path))
    stdout = run_command(cmd, timeout=timeout).stdout
    _LOGGER.debug("%s stdout: %s", _SKOPEO_EXEC_PATH, stdout)


def run_analyzers(path: str, timeout: int = None) -> dict:
    """Run analyzers on the given path (directory) and extract found packages."""
    path = quote(path)

    # In case of Debian-based images we assume dpkg and apt-cache packages are actually executable,
    # meaning the architecture matches with host. We could try to bundle own statically linked binaries
    # and ship them with container to add support for other architectures (if that would be possible).
    deb_packages = _run_dpkg_query(path, timeout=timeout)

    return {
        'mercator': _run_mercator(path, timeout=timeout),
        'rpm': _run_rpm(path, timeout=timeout),
        'rpm-dependencies': _run_rpm_repoquery(path, timeout=timeout),
        'deb': deb_packages,
        'deb-dependencies': _run_apt_cache_show(path, deb_packages, timeout=timeout)
    }
