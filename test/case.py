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

"""Shared classes and utilities across test suite."""

import json
import os


class TestCase:
    """A base class for test cases."""

    DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")

    def get_handler_output(self, handler, subdir):
        """Check output for handlers - yields output and expected output so callee can check all test files present."""
        subdir_path = os.path.join(self.DATA_DIR, subdir)

        for input_file_name in os.listdir(os.path.join(subdir_path, "input")):
            input_file_path = os.path.join(subdir_path, "input", input_file_name)
            output_file_path = os.path.join(
                subdir_path, "output", input_file_name + ".json"
            )

            with open(output_file_path) as output_file:
                expected_output = json.load(output_file)

            with open(input_file_path) as input_file:
                input_content = input_file.read()

            # If assert is done here, pytest for some reason does not report output in a well formatted manner.
            # Return results instead.
            output = handler().run(input_content)
            yield output, expected_output


def raw_and_recover_changes(func):
    """Use Decorator that prevents from modifying library global context."""
    # Prevent from cyclic dependencies.
    from thoth.package_extract.handlers import HandlerBase

    def wrapper(*args, **kwargs):
        base_handlers = HandlerBase.handlers
        HandlerBase.handlers = []
        try:
            func(*args, **kwargs)
        finally:
            HandlerBase.handlers = base_handlers

    return wrapper
