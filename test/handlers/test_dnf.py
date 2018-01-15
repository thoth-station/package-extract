"""Test dnf package installation extraction handler."""
import pytest


class TestDNF:
    """Test dnf package installation extraction handler."""

    @pytest.mark.skip(reason="Currently dnf handler is substituted with yum handler")
    def test_dnf(self):
        pass
