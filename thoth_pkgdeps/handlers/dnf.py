import attr

from .base import HandlerBase


@attr.s
class DNF(HandlerBase):
    """Handle extracting packages from build logs - dnf installer."""

    def run(self, input_text: str) -> dict:
        """Find and parse installed packages and their versions from a build log."""
        return {}


HandlerBase.register(DNF)
