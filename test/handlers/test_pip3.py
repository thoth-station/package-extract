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

"""Test installation of packages using pip3."""

from thoth.package_extract.handlers import HandlerBase
from thoth.package_extract.handlers import PIP3

from ..case import TestCase
from ..case import raw_and_recover_changes


class TestPIP3(TestCase):
    """Test extraction of packages installed via pip3."""

    @raw_and_recover_changes
    def test_run(self):  # noqa D102
        HandlerBase.register(PIP3)
        for output, expected_output in self.get_handler_output(PIP3, "pip3"):
            assert output == expected_output
