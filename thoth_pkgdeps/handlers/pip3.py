"""Parse packages installed using pip3."""

import logging
import re
import typing

import attr

from .base import HandlerBase

_RE_COLLECTING_DEPENDENCY = re.compile(r'Collecting ([+a-zA-Z_\-.():/0-9>=<;"]+)')
_RE_COLLECTING_DEPENDENCY_FROM = re.compile(r'Collecting ([+a-zA-Z_\-.():/0-9>=<;"]+) '
                                            r'\(from ([a-zA-Z_\-.():/0-9>=< ]+)\)')

_LOG = logging.getLogger(__name__)


@attr.s
class PIP3(HandlerBase):
    """Handle extracting packages from build logs - pip3 installer."""

    @staticmethod
    def _do_parse_package(package_specifier: str) -> typing.Tuple[str, typing.Optional[str], typing.Optional[str]]:
        """Parse packages from a report line and return them in a tuple describing also version, version specifier."""
        if package_specifier.startswith('git+'):
            _LOG.warning("Detected installing a Python package from a git repository: %r", package_specifier)
            package_name = package_specifier
            version = 'master'

            # Try to find branch or commit specification.
            split_result = package_specifier.rsplit('@', maxsplit=1)
            if len(split_result) == 2:
                package_name = split_result[0]
                version = split_result[1]

            return package_name, None, version

        # TODO: indirect dependencies have '->'

        # See https://www.python.org/dev/peps/pep-0440/#version-specifiers for all possible values
        for ver_spec in ('~=', '!=', '===', '==', '<=', '>=', '>', '<'):
            split_result = package_specifier.rsplit(ver_spec, maxsplit=1)
            if len(split_result) == 2:
                package_name = split_result[0]
                version = split_result[1]
                return package_name, ver_spec, version

        return package_specifier, None, None

    @classmethod
    def _parse_package(cls, package_specifier: str) -> dict:
        """Parse packages and return them in a dictionary."""
        result = cls._do_parse_package(package_specifier)
        return {
            'package': result[0],
            'version_specifier': result[1],
            'version': result[2]
        }

    @staticmethod
    def _check_entry(result, package_name, package_version):
        """Check parsed entries against reported installed entries by pip after successful installation."""
        matched = [entry for entry in result if entry['package'] == package_name]

        if len(matched) > 1:
            _LOG.warning('Package %r was installed multiple times in versions %s', package_name,
                         tuple(entry['version'] for entry in matched))

        if package_version not in (entry['version'] for entry in matched):
            _LOG.info('Installation of Python package %r using pip with version specifiers %s installed version %s',
                      package_name,
                      [(entry['version_specifier'], entry['version']) for entry in matched],
                      package_version)

    def run(self, input_text: str) -> list:
        """Find and parse installed packages and their versions from a build log."""
        result = []
        for line in input_text.split('\n'):
            match_result = _RE_COLLECTING_DEPENDENCY_FROM.fullmatch(line)
            if match_result:
                dependency = self._parse_package(match_result.group(1))
                dependency['from'] = self._parse_package(match_result.group(2))
                result.append(dependency)
                continue

            match_result = _RE_COLLECTING_DEPENDENCY.fullmatch(line)
            if match_result:
                dependency = self._parse_package(match_result.group(1))
                dependency['from'] = None
                result.append(dependency)
                continue

            if line.startswith('Successfully installed '):
                packages = line[len('Successfully installed '):].split(' ')
                for package in packages:
                    package_name, version = package.rsplit('-', maxsplit=1)
                    self._check_entry(result, package_name, version)
                continue

        return result


HandlerBase.register(PIP3)
