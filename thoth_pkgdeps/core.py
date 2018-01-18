"""Implementation of core routines for thoth-pkgdeps."""

import logging
import os
import typing

from .handlers import HandlerBase
from .image import construct_rootfs
from .image import download_image
from .image import run_analyzers
from .utils import tempdir

_LOGGER = logging.getLogger(__name__)


def extract_buildlog(input_text: str) -> typing.List[dict]:
    """Extract Docker image build log and get all installed packages based on ecosystem."""
    result = []
    for handler in HandlerBase.instantiate_handlers():
        result.append({
            'handler': handler.__class__.__name__.lower(),
            'result': handler.run(input_text)
        })

    return result


def extract_image(image_name: str, timeout: int) -> dict:
    """Extract dependencies from an image."""
    with tempdir() as dir_path:
        download_image(image_name, dir_path, timeout=timeout)

        rootfs_path = os.path.join(dir_path, 'rootfs')
        construct_rootfs(dir_path, rootfs_path)

        return run_analyzers(rootfs_path)
