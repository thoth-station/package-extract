"""Implementation of core routines for thoth-pkgdeps."""

import io
import typing

from thoth_pkgdeps.handlers import HandlerBase


def extract_build_log(input_file: io.TextIOBase) -> typing.List[dict]:
    """Extract Docker image build log and get all installed packages based on ecosystem."""
    result = []
    content = input_file.read()
    for handler in HandlerBase.instantiate_handlers():
        result.append({
            'handler': handler.__class__.__name__.lower(),
            'result': handler.run(content)
        })

    return result
