"""Testing base handler."""

import pytest

from thoth_pkgdeps.handlers import HandlerBase

from ..case import raw_and_recover_changes


class TestHandlerBase:
    """Test :class:thoth_pkgdeps.handlers.HandlerBase."""
    class FooHandler(HandlerBase):
        def run(self, input_text):
            return ["foo"]

    class BarHandler(HandlerBase):
        def run(self, input_text):
            return ["boo"]

    @raw_and_recover_changes
    def test_register(self):
        HandlerBase.register(TestHandlerBase.FooHandler)
        HandlerBase.register(TestHandlerBase.BarHandler)

        assert HandlerBase.get_handler_names() == [TestHandlerBase.FooHandler.__name__,
                                                   TestHandlerBase.BarHandler.__name__]

    @raw_and_recover_changes
    def test_instantiate_handlers(self):
        HandlerBase.register(TestHandlerBase.FooHandler)
        HandlerBase.register(TestHandlerBase.BarHandler)

        instantiated_handlers = list(HandlerBase.instantiate_handlers())
        assert len(instantiated_handlers) == 2
        assert type(instantiated_handlers[0] == TestHandlerBase.FooHandler)
        assert type(instantiated_handlers[0] == TestHandlerBase.BarHandler)

    def test_run(self):
        with pytest.raises(NotImplementedError):
            HandlerBase().run("Foo")

    def test_initial_setup(self):
        assert set(HandlerBase.get_handler_names()) == {'YUM', 'PIP3'}
