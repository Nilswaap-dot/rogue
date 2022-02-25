# SPDX-FileCopyrightText: 2021 Forschungs- und Entwicklungszentrum Fachhochschule Kiel GmbH
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
import time

from rogue import rogue


class TestClient:
    def test_set_value_get_value(self):
        client = rogue.Client("dev0", ports=[rogue.Port("port1"), rogue.Port("port2")])
        client.set_value("port1", "foo")
        client.set_value("port2", 456)
        assert client.get_value("port1") == "foo"
        assert client.get_value("port2") == 456
        client.set_value("port2", "bar")
        assert client.get_value("port2") == "bar"


class TestServerBase:
    @pytest.fixture
    def server(self):
        _server = rogue.ServerBase()
        _server.add_client("dev0", ports=["port0", "port1"])
        _server.add_client("dev1", ports=["port2", "port3"])
        _server.connect(("dev0", "port0"), ("dev1", "port3"))
        return _server

    def test_set_value_get_value(self, server):
        server.set_value("dev0", "port0", 123)
        assert server.get_value("dev0", "port0") == 123
        server.set_value("dev0", "port1", 456)
        server._update()
        server._update()
        server._update()
        assert server.get_value("dev0", "port1") == 456
        assert server.get_value("dev1", "port2") == 0.0
        assert server.get_value("dev1", "port3") == 123

    def test_set_value_no_such_client(self, server):
        with pytest.raises(rogue.RogueException):
            server.set_value("dev3", "port0", None)

    def test_set_value_no_such_port(self, server):
        with pytest.raises(rogue.RogueException):
            server.set_value("dev0", "port2", None)

    def test_set_value_no_such_client(self, server):
        with pytest.raises(rogue.RogueException):
            server.get_value("dev3", "port0")

    def test_set_value_no_such_port(self, server):
        with pytest.raises(rogue.RogueException):
            server.get_value("dev0", "port2")

    def test_listen_data(self, server):
        counter = 0

        def loop(client):
            nonlocal counter
            client.set_value("port0", counter**2)
            counter += 1

        server.add_client("dev2", {"port0": 0}, loop)
        server.listen("dev2", "port0")
        for _ in range(3):
            server._update()
        assert server.data == {"dev2": {"port0": rogue.Data([0, 1, 2], [0, 1, 4])}}


def _sleep(duration: float) -> float:
    """Sleep _at least_ for the specified duration and return actual
    sleep duration."""
    # Python gives no guarantee how long `time.sleep` actually suspends
    # operation, so we measure actual sleep time:
    # https://docs.python.org/3.8/library/time.html#time.sleep
    start = time.perf_counter()
    while (time_slept := time.perf_counter() - start) < duration:
        time.sleep(duration - time_slept)
    return time_slept


class TestDaemon:
    def test_success(self):
        duration = 0.01
        counter = 0

        def fn():
            nonlocal counter
            counter += 1

        daemon = rogue.Daemon(target=fn, duration=duration)
        daemon.start()
        time_slept = _sleep(0.015)
        daemon.kill()
        daemon.process_errors()
        assert counter == 1 + int(time_slept / duration)

    def test_failure(self):
        def fn():
            raise RuntimeError()

        daemon = rogue.Daemon(target=fn, duration=0.0)
        daemon.start()
        daemon.kill()
        with pytest.raises(RuntimeError):
            daemon.process_errors()


class TestServer:
    @pytest.fixture
    def server(self):
        _server = rogue.Server(duration=0.01)
        _server.add_client("dev0", ports=["port0", "port1"])
        _server.add_client("dev1", ports=["port2", "port3"])
        _server.connect(("dev0", "port0"), ("dev1", "port3"))
        yield _server
        _server.kill()
        _server.process_errors()

    def test_set_value_get_value(self, server):
        server.exec()
        server.set_value("dev0", "port0", 123)
        server.set_value("dev0", "port1", 456)
        _sleep(0.02)
        server.process_errors()
        assert server.get_value("dev0", "port0") == 123
        assert server.get_value("dev0", "port1") == 456
        assert server.get_value("dev1", "port2") == 0.0
        assert server.get_value("dev1", "port3") == 123
        server.process_errors()

    def test_set_value_no_such_client(self, server):
        server.exec()
        with pytest.raises(rogue.RogueException):
            server.set_value("dev2", "port0", None)

    def test_set_value_no_such_port(self, server):
        server.exec()
        with pytest.raises(rogue.RogueException):
            server.set_value("dev0", "port2", None)

    def test_set_value_no_such_client(self, server):
        server.exec()
        with pytest.raises(rogue.RogueException):
            server.get_value("dev2", "port0")

    def test_set_value_no_such_port(self, server):
        server.exec()
        with pytest.raises(rogue.RogueException):
            server.get_value("dev0", "port2")

    def test_listen_data(self, server):
        counter = 0

        def loop(client):
            nonlocal counter
            client.set_value("port0", counter**2)
            counter += 1

        server.add_client("dev2", {"port0": 0}, loop)
        server.listen("dev2", "port0")
        server.exec()
        _sleep(0.1)
        server.kill()
        data = server.data["dev2"]["port0"]
        trunc = rogue.Data(data.time[:4], data.values[:4])
        trunc.time = [round(t, 2) for t in trunc.time]
        print(trunc.time)
        assert trunc == rogue.Data([0.0, 0.01, 0.02, 0.03], [0, 1, 4, 9])
        server.process_errors()

    def test_restart(self):
        server = rogue.Server()
        server.exec()
        _sleep(0.09)
        server.kill()
        assert server._cycle_count == 0
        server.exec()
        _sleep(0.01)
        server.process_errors()
