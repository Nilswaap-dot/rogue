import pytest

from rogue import rogue


class TestClient:

    def test_set_value_get_value(self):
        client = rogue.Client(ports=[rogue.Port('port1'), rogue.Port('port2')])
        client.set_value('port1', 'foo')
        client.set_value('port2', 456)
        assert client.get_value('port1') == 'foo'
        assert client.get_value('port2') == 456
        client.set_value('port2', 'bar')
        assert client.get_value('port2') == 'bar'


class TestServer:
    pass
