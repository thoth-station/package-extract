import re

import attr

from .base import HandlerBase

_RE_DEPENDENCY = re.compile(r'Collecting ([a-zA-Z_\-.():/0-9>=<;" ]+) \(from ([a-zA-Z_\-.():/0-9>=< ]+)\)')


@attr.s
class PIP3(HandlerBase):
    """Handle extracting packages from build logs - pip3 installer."""

    def run(self, input_text: str) -> dict:
        """Find and parse installed packages and their versions from a build log."""
        result = []
        for line in input_text.split('\n'):
            match_result = _RE_DEPENDENCY.fullmatch(line)
            if match_result:
                # TODO: implement parsing
                result.append((match_result.group(1), match_result.group(2)))

            # TODO: what about something like:
            # pip3 install git+https://github.com/fridex/thoth-pkgdeps@master
            # Collecting git+https://github.com/fridex/thoth-pkgdeps@master

        # TODO: check against 'Successfully installed' line in pip3 output
        return result


HandlerBase.register(PIP3)
