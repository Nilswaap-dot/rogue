import pytest
import time

from rogue import rogue


class TestClient:

    def test_set_value_get_value(self):
        client = rogue.Client('dev0', ports=[rogue.Port('port1'), rogue.Port('port2')])
        client.set_value('port1', 'foo')
        client.set_value('port2', 456)
        assert client.get_value('port1') == 'foo'
        assert client.get_value('port2') == 456
        client.set_value('port2', 'bar')
        assert client.get_value('port2') == 'bar'


class TestServerBase:

    @pytest.fixture
    def server(self):
        _server = rogue.ServerBase()
        _server.add_client('dev0', ports=['port0', 'port1'])
        _server.add_client('dev1', ports=['port2', 'port3'])
        _server.connect(('dev0', 'port0'), ('dev1', 'port3'))
        return _server

    def test_set_value_get_value(self, server):
        server.set_value('dev0', 'port0', 123)
        server.set_value('dev0', 'port1', 456)
        server._update()
        assert server.get_value('dev0', 'port0') == 123
        assert server.get_value('dev0', 'port1') == 456
        assert server.get_value('dev1', 'port2') == 0.0
        assert server.get_value('dev1', 'port3') == 123

    def test_set_value_no_such_client(self, server):
        with pytest.raises(KeyError):
            server.set_value('dev3', 'port0', None)

    def test_set_value_no_such_port(self, server):
        with pytest.raises(KeyError):
            server.set_value('dev0', 'port2', None)

    def test_set_value_no_such_client(self, server):
        with pytest.raises(KeyError):
            server.get_value('dev3', 'port0')

    def test_set_value_no_such_port(self, server):
        with pytest.raises(KeyError):
            server.get_value('dev0', 'port2')


class TestDaemon:

    def test_success(self):
        counter = 0
        def fn():
            nonlocal counter
            counter += 1
        daemon = rogue.Daemon(target=fn, grain=0.01)
        daemon.start()
        time.sleep(0.015)
        daemon.kill()
        daemon.process_errors()
        assert counter == 2

    def test_failure(self):
        def fn():
            raise RuntimeError()
        daemon = rogue.Daemon(target=fn, grain=0.0)
        daemon.start()
        daemon.kill()
        with pytest.raises(RuntimeError):
            daemon.process_errors()


class TestServer:

    @pytest.fixture
    def server(self):
        _server = rogue.Server(grain=0.01)
        _server.add_client('dev0', ports=['port0', 'port1'])
        _server.add_client('dev1', ports=['port2', 'port3'])
        _server.connect(('dev0', 'port0'), ('dev1', 'port3'))
        _server.exec()
        yield _server
        _server.kill()

    def test_set_value_get_value(self, server):
        server.set_value('dev0', 'port0', 123)
        server.set_value('dev0', 'port1', 456)
        time.sleep(0.02)
        server.process_errors()
        assert server.get_value('dev0', 'port0') == 123
        assert server.get_value('dev0', 'port1') == 456
        assert server.get_value('dev1', 'port2') == 0.0
        assert server.get_value('dev1', 'port3') == 123

    def test_set_value_no_such_client(self, server):
        with pytest.raises(KeyError):
            server.set_value('dev2', 'port0', None)

    def test_set_value_no_such_port(self, server):
        with pytest.raises(KeyError):
            server.set_value('dev0', 'port2', None)

    def test_set_value_no_such_client(self, server):
        with pytest.raises(KeyError):
            server.get_value('dev2', 'port0')

    def test_set_value_no_such_port(self, server):
        with pytest.raises(KeyError):
            server.get_value('dev0', 'port2')
