"""Exception hierarchy in thoth-pkgdeps tool."""


class ThothPkgdepsException(Exception):
    """A base exception in the thoth-pkgdeps exception hierarchy."""


class InvalidImageError(ThothPkgdepsException):
    """Raised on invalid Docker image."""


class NotSupported(ThothPkgdepsException):
    """Raised on requesting an unsupported operation."""


class TimeoutExpired(ThothPkgdepsException):
    """Raised on command timeout."""
