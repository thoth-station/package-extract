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
