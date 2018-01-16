"""Test installation of packages using yum."""

from thoth_pkgdeps.handlers import HandlerBase
from thoth_pkgdeps.handlers import YUM

from ..case import TestCase
from ..case import raw_and_recover_changes


class TestYUM(TestCase):
    """Test installing packages using yum."""

    @raw_and_recover_changes
    def test_run(self):
        HandlerBase.register(YUM)
        for output, expected_output in self.get_handler_output(YUM, 'yum'):
            assert output == expected_output
