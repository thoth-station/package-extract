"""Extraction of installed packages for project Thoth."""

from .core import extract_buildlog
from .core import extract_image

from thoth.common import __version__ as __common__version__
from thoth.analyzer import __version__ as __analyzer__version__

__version__ = f"1.0.1+common.{__common__version__}.analyzer.{__analyzer__version__}"

__title__ = 'thoth-package-extract'
__author__ = 'Fridolin Pokorny'
__license__ = 'GPLv3+'
__copyright__ = 'Copyright 2018 Fridolin Pokorny'
