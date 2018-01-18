"""Implementation of core routines for thoth-pkgdeps."""

import typing

from thoth_pkgdeps.handlers import HandlerBase


def extract_buildlog(input_text: str) -> typing.List[dict]:
    """Extract Docker image build log and get all installed packages based on ecosystem."""
    result = []
    for handler in HandlerBase.instantiate_handlers():
        result.append({
            'handler': handler.__class__.__name__.lower(),
            'result': handler.run(input_text)
        })

    return result
