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

"""Exception hierarchy in thoth-package-extract tool."""


class ThothPkgdepsException(Exception):
    """A base exception in the thoth-package-extract exception hierarchy."""


class InvalidImageError(ThothPkgdepsException):
    """Raised on invalid Docker image."""


class NotSupported(ThothPkgdepsException):
    """Raised on requesting an unsupported operation."""


class TimeoutExpired(ThothPkgdepsException):
    """Raised on command timeout."""
