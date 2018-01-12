import attr
import re

from .base import HandlerBase

_RE_DEPENDENCY = re.compile(r'--> Processing Dependency: '
                            r'([a-zA-Z_\-.():/0-9>=< ]+) for package: ([a-zA-Z_\-.():0-9]+)')


@attr.s
class YUM(HandlerBase):
    """Handle extracting packages from build logs - yum installer."""

    def run(self, input_text: str) -> dict:
        """Find and parse installed packages and their versions from a build log."""
        result = []

        for line in input_text.split('\n'):
            line.strip()

            match_result = _RE_DEPENDENCY.fullmatch(line)
            if match_result is not None:
                # TODO: implement parsing
                result.append((match_result.group(1), match_result.group(2)))

        # TODO: check against the final table in yum output

        return result


HandlerBase.register(YUM)
