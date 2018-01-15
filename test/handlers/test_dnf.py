import pytest


class TestDNF:
    @pytest.mark.skip(reason="Currently dnf handler is substituted with yum handler")
    def test_dnf(self):
        pass
