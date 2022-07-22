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

"""Manipulation with an image and image scanning."""

import json
import logging
import os
import tarfile
import typing
import stat
from shlex import quote
import hashlib
from pathlib import Path
import glob
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Generator
from typing import Optional
from collections import deque

import toml
from thoth.analyzer import run_command
from thoth.common import cwd
from pip._internal.operations.freeze import freeze

from .exceptions import InvalidImageError
from .exceptions import NotSupported
from .rpmlib import parse_nvra

_LOGGER = logging.getLogger(__name__)
_HERE_DIR = os.path.dirname(os.path.abspath(__file__))
_SKOPEO_EXEC_PATH = os.getenv(
    "SKOPEO_EXEC_PATH", os.path.join(_HERE_DIR, "bin", "skopeo")
)
_MAX_SYMLINKS = 50


def _parse_repoquery(output: str) -> dict:
    """Parse repoquery output."""
    result: dict = {}

    package = None
    for line in output.split("\n"):
        line = line.strip()

        if not line:
            continue

        if line.startswith("package: "):
            package = line[len("package: ") :]
            if package in result:
                _LOGGER.warning(
                    "Package %r was already stated in the repoquery output, "
                    "dependencies will be appended",
                    package,
                )
                continue
            result[package] = []
        elif line.startswith("dependency: "):
            if not package:
                _LOGGER.error(
                    "Stated dependency %r has no package associated (parser error?), this error is not fatal",
                    package,
                )
            result[package].append(line[len("dependency: ") :])

    return result


def _run_rpm_repoquery(path: str, timeout: int = None) -> list:
    """Run repoquery and return it's output (parsed)."""
    cmd = "repoquery --deplist --installed --installroot {!r}".format(path)
    output = _parse_repoquery(run_command(cmd, timeout=timeout).stdout)

    result = []
    for package_identifier, dependencies in output.items():
        rpm_package = parse_nvra(package_identifier)

        rpm_package["dependencies"] = dependencies
        rpm_package["epoch"] = rpm_package["epoch"] or None
        rpm_package["package_identifier"] = package_identifier
        result.append(rpm_package)

    return result


def _run_rpm(path: str, timeout: int = None) -> typing.List[str]:
    """Query for installed rpm packages in the given root described by path."""
    cmd = "rpm -qa --root {!r}".format(path)
    output = run_command(cmd, timeout=timeout).stdout
    packages = output.split("\n")
    if not packages[-1]:
        packages.pop()
    return packages


def _run_dpkg_query(path: str, timeout: int = None) -> typing.List[dict]:
    """Query for installed deb packages in the given root."""
    # Make sure dpkg-query exist, give up if not.
    dpkg_query_path = os.path.join(path, "usr", "bin", "dpkg-query")
    if not os.path.isfile(dpkg_query_path):
        _LOGGER.info(
            "Binary dpkg-query not found, deb packages discovery will not be performed"
        )
        return []

    # Make sure dpkg-query is executable after extraction.
    st = os.stat(dpkg_query_path)
    os.chmod(dpkg_query_path, st.st_mode | stat.S_IEXEC)

    cmd = "fakeroot fakechroot /usr/sbin/chroot {!r} /usr/bin/dpkg-query -l".format(
        path
    )
    output = run_command(cmd, timeout=timeout).stdout
    result = []
    for line in output.split("\n"):
        if not line.startswith("ii "):
            _LOGGER.debug("Skipping line (not an installed package): %r", line)
            continue

        parts = line.split(maxsplit=4)
        if len(parts) < 4:
            _LOGGER.warning(
                "Line in dpkg-query output does not provide enough information to parse package name, "
                "version and architecture: %s",
                line,
            )
            continue

        result.append({"name": parts[1], "version": parts[2], "arch": parts[3]})

    return result


def _parse_deb_dependency_line(
    line_str: str,
) -> typing.List[typing.Tuple[typing.Any, typing.Any]]:
    """Parse deb dependency line respecting name of package and the given version range provided."""
    result = []
    for entry in line_str.split(", "):
        parts = entry.split(" (", maxsplit=1)
        if len(parts) == 2:
            result.append((parts[0], parts[1][:-1]))  # -1 to remove ending ')'
        else:
            # No version range specification defined.
            result.append((parts[0], ""))
    return result


def _gather_python_file_digests(path: str) -> typing.List[dict]:
    """Calculate checksum for all Python files inside image."""
    digests = []
    for root, dirs, files in os.walk(path):
        for file_ in files:
            if file_.endswith(".py"):
                filepath = os.path.join(root, file_)
                if os.path.isfile(filepath):
                    digest = hashlib.sha256()
                    with open(filepath, "rb") as afile:
                        digest.update(afile.read())
                    digests.append(
                        {
                            "filepath": filepath[len(path) :],
                            "sha256": digest.hexdigest(),
                        }
                    )
    return digests


def _gather_os_info(path: str) -> dict:
    """Gather information about operating system used."""
    result: dict = {}
    os_release_file = Path(path) / "etc/os-release"
    if os_release_file.exists():
        try:
            content = os_release_file.read_text()
        except Exception as exc:
            _LOGGER.warning(
                "Failed to read /etc/os-release file to gather operating system information: %s",
                str(exc),
            )
            return result

        for line in content.splitlines():
            parts = line.split("=", maxsplit=1)
            if len(parts) != 2:
                continue

            key = parts[0].lower()
            value = parts[1].strip('"')

            result[key] = value

    return result


def _run_apt_cache_show(
    path: str, deb_packages: typing.List[dict], timeout: int = None
) -> list:
    """Gather information about packages and their dependencies."""
    # Make sure dpkg-query exist, give up if not.
    if not deb_packages:
        return []

    apt_cache_path = os.path.join(path, "usr", "bin", "apt-cache")
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
        cmd = "fakeroot fakechroot /usr/sbin/chroot {!r} /usr/bin/apt-cache show {}={}".format(
            path, record["name"], record["version"]
        )

        # Do not touch original deb query, extend it rather with more info to follow rpm schema.
        entry = dict(record)
        parts = entry["version"].split(":", maxsplit=1)
        if len(parts) == 2:
            try:
                # If it parses int, its an epoch probably.
                int(parts[0])
                entry["epoch"] = parts[0]
                entry["version"] = parts[1]
            except ValueError:
                entry["epoch"] = None

        output = run_command(cmd, timeout=timeout).stdout
        entry["pre-depends"], entry["depends"], entry["replaces"] = [], [], []
        for line in output.splitlines():
            if line.startswith("Pre-Depends: "):
                deps = _parse_deb_dependency_line(line[len("Pre-Depends: ") :])
                entry["pre-depends"] = [{"name": d[0], "version": d[1]} for d in deps]
            elif line.startswith("Depends: "):
                deps = _parse_deb_dependency_line(line[len("Depends: ") :])
                entry["depends"] = [{"name": d[0], "version": d[1]} for d in deps]
            elif line.startswith("Replaces: "):
                deps = _parse_deb_dependency_line(line[len("Replaces: ") :])
                entry["replaces"] = [{"name": d[0], "version": d[1]} for d in deps]

        result.append(entry)

    return result


def _get_lib_dir_symbols(result: dict, container_path: str, path: str) -> None:
    """Get library symbols from a directory."""
    path = path[1:] if path.startswith("/") else path
    for so_file_path in glob.glob(os.path.join(container_path, path, "*.so*")):
        # We grep for '0 A' here because all exported symbols are outputted by nm like:
        # 00000000 A GLIBC_1.x or:
        # 0000000000000000 A GLIBC_1.x
        command = f"nm -D {so_file_path!r} | grep '0 A'"

        # Drop path to the extracted container in the output.
        so_file_path = so_file_path[len(container_path) :]

        _LOGGER.debug("Gathering symbols from %r", so_file_path)
        command_result = run_command(command, timeout=120, raise_on_error=False)
        if command_result.return_code != 0:
            _LOGGER.warning(
                "Failed to obtain library symbols from %r; stderr: %s, stdout: %s",
                so_file_path,
                command_result.stderr,
                command_result.stdout,
            )
            continue

        if so_file_path not in result:
            result[so_file_path] = set()

        for line in command_result.stdout.splitlines():
            columns = line.split(" ")
            if len(columns) > 2:
                result[so_file_path].add(columns[2])


def _ld_config_entries(path: str) -> Generator[str, None, None]:
    """Iterate over entries in ld.so.conf, recursively."""
    stack = deque([("etc", "ld.so.conf")])

    while stack:
        relative_path, conf_file = stack.pop()
        try:
            with open(os.path.join(path, relative_path, conf_file), "r") as f:
                for line in f.readlines():
                    if line.startswith("include "):
                        line = line[len("include ") :]
                        # Includes are relative to /etc/
                        if not line.startswith("/"):
                            line = os.path.join("etc", line)

                    if not line:
                        continue

                    if line.startswith("/"):
                        to_glob = os.path.join(path, line[1:])
                    else:
                        to_glob = os.path.join(path, relative_path, line)

                    for entry_path in glob.glob(to_glob):
                        if os.path.isdir(entry_path):
                            yield line
                        elif os.path.isfile(entry_path):
                            # ld.so.conf can point to another configuration files.
                            # "foo/nar"
                            stack.append(
                                (
                                    os.path.dirname(
                                        os.path.join(relative_path, conf_file)
                                    ),
                                    os.path.basename(entry_path),
                                )
                            )
                        else:
                            _LOGGER.warning(
                                "Skipping entry %r from symbols extraction not a file or directory",
                                line,
                            )
        except Exception as exc:
            _LOGGER.warning(
                "Failed to analyze file %r for available symbols: %s",
                conf_file,
                str(exc),
            )


def _ld_config_symbols(result: dict, path: str) -> None:
    """Gather library symbols based on ld.so.conf."""
    _LOGGER.debug("Gathering symbols based on ld.so.conf file")
    for entry in _ld_config_entries(path):
        try:
            _get_lib_dir_symbols(result, path, entry)
        except Exception as exc:
            _LOGGER.warning(
                "Cannot load symbols from %r (based on ld.so.conf configuration): %s",
                entry,
                str(exc),
            )


def _ld_env_symbols(result: dict, path: str) -> None:
    """Gather library symbols based on entries in LD_LIBRARY_PATH environment variable."""
    ld_paths = os.getenv("LD_LIBRARY_PATH")

    if ld_paths is None:
        _LOGGER.debug("No LD_LIBRARY_PATH detected to gather system symbols")
        return

    for p in ld_paths.split(":"):
        _get_lib_dir_symbols(result, path, p[1:])


def _get_system_symbols(path: str) -> Dict[str, List[str]]:
    """Get library symbols found in relevant directories, configuration and environment variables."""
    result: dict = {}
    _get_lib_dir_symbols(result, path, "usr/lib64")
    _get_lib_dir_symbols(result, path, "lib64")
    _get_lib_dir_symbols(result, path, "usr/lib32")
    _get_lib_dir_symbols(result, path, "lib32")
    _get_lib_dir_symbols(result, path, "usr/lib")
    _get_lib_dir_symbols(result, path, "lib")
    _ld_config_symbols(result, path)
    # XXX: Commented out as we need to handle environment variables for this during container image extraction.
    # _ld_env_symbols(result, path)
    # Convert to list as a result, also good for serialization into JSON happening later on.
    return {path: list(symbols) for path, symbols in result.items()}


def _get_layer_digest_v1(layer_def: dict):
    """Get digest of a layer for v1 container image format."""
    return layer_def["blobSum"].split(":", maxsplit=1)[-1]


def _get_layer_digest_v2(layer_def: dict):
    """Get digest of a layer for v2 container image format."""
    return layer_def["digest"].split(":", maxsplit=1)[-1]


def construct_rootfs(dir_path: str, rootfs_path: str) -> list:
    """Construct rootfs in a directory by extracting layers."""
    os.makedirs(rootfs_path, exist_ok=True)

    try:
        with open(os.path.join(dir_path, "manifest.json")) as manifest_file:
            manifest = json.load(manifest_file)
    except FileNotFoundError as exc:
        raise InvalidImageError(
            "No manifest.json file found in the downloaded "
            "image in {}".format(os.path.join(dir_path, "manifest.json"))
        ) from exc

    if manifest.get("schemaVersion") == 1:
        manifest_layers = manifest["fsLayers"]
        get_layer_digest = _get_layer_digest_v1
    elif manifest.get("schemaVersion") == 2:
        manifest_layers = manifest["layers"]
        get_layer_digest = _get_layer_digest_v2
    else:
        raise NotSupported(
            "Invalid schema version in manifest.json file: {} "
            "(currently supported are schema versions 1 and 2)".format(
                manifest.get("schemaVersion")
            )
        )

    layers = []
    _LOGGER.debug("Layers found: %r", manifest_layers)
    for layer_def in manifest_layers:
        layer_digest = get_layer_digest(layer_def)

        _LOGGER.debug("Extracting layer %r", layer_digest)
        layers.append(layer_digest)

        layer_gzip_tar = os.path.join(dir_path, layer_digest)
        with cwd(rootfs_path):
            tar_file = tarfile.open(layer_gzip_tar, "r:gz")

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
                        _LOGGER.exception(
                            "Failed to extract %r, exception is not fatal: %s",
                            member.name,
                            exc,
                        )

    return layers


def _get_absolute_link(
    root_path: str, path: str, iter: int
) -> Tuple[Optional[str], bool]:
    """Find the absolute link of the given link."""
    if iter > _MAX_SYMLINKS:
        _LOGGER.warning("Maximum symlink traversal reached.")
        return None, True
    elif os.path.islink(path):
        next_path = os.path.normpath(os.path.join(root_path, os.readlink(path)))
        abs_link, _ = _get_absolute_link(root_path, next_path, iter + 1)
        return abs_link, True
    else:
        if not os.path.isfile(path):
            _LOGGER.warning(
                "Python link refers to %s, but this file is not present on filesystem.",
                path,
            )
        return path, False


def _get_python_interpreters(path: str) -> List[dict]:
    """Find all python interpreters and symlinks."""
    result = []

    for py_path in glob.glob("{}/usr/bin/python*".format(path)):
        version_ = None
        try:
            os.chmod(py_path, stat.S_IEXEC)
            line = run_command("{} --version".format(py_path), timeout=2).stdout
            parts = line.split(maxsplit=2)
            if len(parts) == 2 and parts[0] == "Python":
                version_ = line.rstrip()
        except Exception as exc:
            _LOGGER.warning(
                "Failed to run %s --version to gather python interpreter version: %s",
                py_path,
                str(exc),
            )

        absolute_link, is_file_present = _get_absolute_link(path, py_path, 0)
        if absolute_link is not None:
            if not is_file_present:
                absolute_link = absolute_link[len(path) :]

        py_interpret = {
            "path": py_path[len(path) :],
            "link": absolute_link,
            "version": version_,
        }

        result.append(py_interpret)

    return result


def download_image(
    image_name: str,
    dir_path: str,
    timeout: int = None,
    registry_credentials: str = None,
    tls_verify: bool = True,
) -> None:
    """Download an image to dir_path."""
    _LOGGER.debug("Downloading image %r", image_name)

    cmd = f"{_SKOPEO_EXEC_PATH} copy "
    if not tls_verify:
        cmd += "--src-tls-verify=false "
    if registry_credentials:
        cmd += "--src-creds={} ".format(quote(registry_credentials))

    cmd += "docker://{} dir:/{}".format(quote(image_name), quote(dir_path))
    stdout = run_command(cmd, timeout=timeout).stdout
    _LOGGER.debug("%s stdout: %s", _SKOPEO_EXEC_PATH, stdout)


def get_image_size(path: str) -> int:
    """Calculate the size of the image."""
    total_size = 0
    for path_, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(path, f)
            total_size += os.path.getsize(fp)
    return total_size


def _get_cuda_version(path: str) -> dict:
    """Get the cuda version."""
    res = {}
    # Gathering version from version.txt file
    version_path = os.path.join(path, "usr/local/cuda/version.txt")
    if os.path.isfile(version_path):
        with open(version_path, "r") as f:
            for line in f.readlines():
                if line.startswith("CUDA Version"):
                    res["/usr/local/cuda/version.txt"] = line[
                        len("CUDA Version") :
                    ].strip()
                    break
        if res.get("/usr/local/cuda/version.txt") is not None:
            _LOGGER.info(
                "CUDA version %s was identified in file version.txt",
                res["/usr/local/cuda/version.txt"],
            )
        else:
            _LOGGER.warning("No CUDA version identifier was found in file version.txt")
    else:
        _LOGGER.info("No version.txt file was found to detect CUDA version")

    # Gathering version from nvcc command
    nvcc_path = os.path.join(path + "/usr/local/cuda/bin/nvcc")
    if os.path.exists(nvcc_path):
        st = os.stat(nvcc_path)
        os.chmod(nvcc_path, st.st_mode | stat.S_IEXEC)
        result = run_command("{} --version".format(nvcc_path), raise_on_error=False)
        if result.return_code != 0:
            _LOGGER.warning(
                "Unable to detect CUDA version - nvcc returned non-zero exit code: %s",
                result.to_dict(),
            )
        else:
            for line in result.stdout.splitlines():
                version = line.rsplit(", ", maxsplit=1)[-1]
                if line.startswith("Cuda compilation tools") and version.startswith(
                    "V"
                ):
                    res["nvcc_version"] = version[1:]
                    break
            if res.get("nvcc_version") is not None:
                _LOGGER.info(
                    "Detected CUDA version %s from nvcc output", res["nvcc_version"]
                )
            else:
                _LOGGER.debug(
                    "Unable to detect CUDA version from nvcc output: %r", result.stdout
                )
    else:
        _LOGGER.info("No nvcc executable was found to detect CUDA version")

    return res


def _gather_skopeo_inspect(path, timeout) -> Dict[str, str]:
    """Gether information from skopeo inspect."""
    path = os.path.dirname(path)  # Remove rootfs.
    cmd = f"{_SKOPEO_EXEC_PATH} inspect dir:{path}"
    output = run_command(cmd, timeout=timeout, is_json=True).stdout
    return output


def _get_python_packages(path: str) -> List[Dict[str, Any]]:
    """Get installed Python packages in the container image."""
    _LOGGER.debug("Detecting installed Python packages")
    result = []
    for location, _, _ in os.walk(path):
        if os.path.basename(location) != "site-packages":
            _LOGGER.debug(
                "Excluding %r from checking Python modules installed: not a site-packages directory",
                location,
            )
            continue

        for dist in freeze(paths=[location]):
            package_name, package_version = dist.split("==", maxsplit=1)
            result.append(
                {
                    "package_name": package_name,
                    "package_version": package_version,
                    "location": location[len(path) :]
                    if location.startswith(path)
                    else location,
                }
            )

    return result


def _get_aicoe_ci(path: str) -> Dict[str, Any]:
    """Obtain information propagated from AICoE-CI during the image build."""
    aicoe_ci_path = os.path.join(path, "opt", "aicoe-ci")

    pipfile_content = None
    pipfile_path = os.path.join(aicoe_ci_path, "Pipfile")
    if os.path.exists(pipfile_path):
        try:
            with open(pipfile_path) as f:
                pipfile_content = toml.load(f)
        except Exception:
            _LOGGER.exception(
                "Failed to obtain dependency information from Pipfile located at %r",
                pipfile_path,
            )

    pipfile_lock_content = None
    pipfile_lock_path = os.path.join(aicoe_ci_path, "Pipfile.lock")
    if os.path.exists(pipfile_lock_path):
        try:
            with open(pipfile_lock_path) as f:
                pipfile_lock_content = json.load(f)
        except Exception:
            _LOGGER.exception(
                "Failed to obtain dependency information from Pipfile.lock located at %r",
                pipfile_lock_path,
            )

    return {
        "requirements": pipfile_content,
        "requirements_lock": pipfile_lock_content,
    }


def run_analyzers(path: str, timeout: int = None) -> dict:
    """Run analyzers on the given path (directory) and extract found packages."""
    path = quote(path)

    # In case of Debian-based images we assume dpkg and apt-cache packages are actually executable,
    # meaning the architecture matches with host. We could try to bundle own statically linked binaries
    # and ship them with container to add support for other architectures (if that would be possible).
    deb_packages = _run_dpkg_query(path, timeout=timeout)

    return {
        "rpm": _run_rpm(path, timeout=timeout),
        "rpm-dependencies": _run_rpm_repoquery(path, timeout=timeout),
        "deb": deb_packages,
        "deb-dependencies": _run_apt_cache_show(path, deb_packages, timeout=timeout),
        "python-files": _gather_python_file_digests(path),
        "operating-system": _gather_os_info(path),
        "skopeo-inspect": _gather_skopeo_inspect(path, timeout=timeout),
        "system-symbols": _get_system_symbols(path),
        "python-interpreters": _get_python_interpreters(path),
        "cuda-version": _get_cuda_version(path),
        "python-packages": _get_python_packages(path),
        "aicoe-ci": _get_aicoe_ci(path),
    }
