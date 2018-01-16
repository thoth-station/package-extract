"""Test installation of packages using pip3"""

from thoth_pkgdeps.handlers import HandlerBase
from thoth_pkgdeps.handlers import PIP3

from ..case import TestCase
from ..case import raw_and_recover_changes


class TestPIP3(TestCase):
    """Test extraction of packages installed via pip3."""

    @raw_and_recover_changes
    def test_run(self):
        HandlerBase.register(PIP3)
        for output, expected_output in self.get_handler_output(PIP3, 'pip3'):
            assert output == expected_output
