#!/usr/bin/env python3
# thoth-package-extract
# Copyright(C) 2018, 2019, 2020 Fridolin Pokorny
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Test installation of packages using yum."""

from thoth.package_extract.handlers import HandlerBase
from thoth.package_extract.handlers import YUM

from ..case import TestCase
from ..case import raw_and_recover_changes


class TestYUM(TestCase):
    """Test installing packages using yum."""

    @raw_and_recover_changes
    def test_run(self):  # noqa: D102
        HandlerBase.register(YUM)
        for output, expected_output in self.get_handler_output(YUM, "yum"):
            assert output == expected_output
