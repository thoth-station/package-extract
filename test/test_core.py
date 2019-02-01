#!/usr/bin/env python3
# thoth-package-extract
# Copyright(C) 2018, 2019 Fridolin Pokorny
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

"""Test core routines of thoth-package-extract."""


from thoth.package_extract.core import extract_buildlog
from thoth.package_extract.handlers import HandlerBase

from .case import raw_and_recover_changes


_TEST_INPUT = """foo\tbar\tbar\tbaz"""


class _FooHandler(HandlerBase):
    """Testing dummy handler."""
    def run(self, input_text):
        return input_text.split('\t')


@raw_and_recover_changes
def test_extract_build_log():
    HandlerBase.register(_FooHandler)

    result = extract_buildlog(_TEST_INPUT)
    assert result == [{
        'handler': _FooHandler.__name__.lower(),
        'result': ['foo', 'bar', 'bar', 'baz']
    }]
