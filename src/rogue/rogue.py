# SPDX-FileCopyrightText: 2021 Forschungs- und Entwicklungszentrum Fachhochschule Kiel GmbH
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import dataclasses
import queue
import threading
import time
from typing import Callable, Optional


class Client:

    def __init__(self, id: str, ports: list[Port], loop: Optional[Callable] = None):
        self._id = id
        self._ports = {elem.id: elem for elem in ports}
        if loop is None:
            self._loop = lambda _: ...

    @property
    def id(self) -> str:
        return self._id

    @property
    def ports(self) -> list[str]:
        return list(self._ports)

    def set_value(self, port: str, value: Any) -> None:
        self._ports[port].value = value

    def get_value(self, port: str) -> None:
        return self._ports[port].value

    def loop(self) -> None:
        self._loop(self)


class Port:

    def __init__(self, id: str, value: Any = 0.0):
        self._id = id
        self._value = value

    @property
    def id(self) -> str:
        return self._id

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


@dataclasses.dataclass(frozen=True)
class Jack:
    client: str
    port: str


@dataclasses.dataclass(frozen=True)
class Connection:
    sender: Jack
    receiver: Jack


class ServerBase:

    def __init__(self):
        self._clients = {}
        self._connections = set()
        self._lock = threading.Lock()
        self._data = {}
        self._cycle_count = 0

    def add_client(self, id: str, ports: Union[list[str], dict[str, Any]]) -> None:
        with self._lock:
            if isinstance(ports, list):
                self._clients[id] = Client(id, [Port(id) for id in ports])
            else:
                self._clients[id] = Client(id, [Port(id, val) for id, val in ports.items()])
            self._data[id] = {port: [] for port in ports}

    def connect(self,
                sender: tuple[str, str],
                receiver: tuple[str, str]) -> None:
        with self._lock:
            sender, receiver = Jack(*sender), Jack(*receiver)
            c = Connection(sender, receiver)
            self._connections.add(c)

    def set_value(self, client: str, port: str, value: Any) -> None:
        with self._lock:
            self._clients[client].set_value(port, value)

    def get_value(self, client: str, port: str):
        with self._lock:
            return self._clients[client].get_value(port)

    def _update(self):
        with self._lock:
            for _, client in self._clients.items():
                client.loop()
            for conn in self._connections:
                sender = self._clients[conn.sender.client]
                receiver = self._clients[conn.receiver.client]
                receiver.set_value(
                    conn.receiver.port,
                    sender.get_value(conn.sender.port)
                )
        for _, client in self._clients.items():
            for port in client.ports:
                self._data[client.id][port].append((self._cycle_count, client.get_value(port)))
        self._cycle_count += 1


class Daemon(threading.Thread):

    def __init__(self, *args, grain: float, **kwargs):
        super().__init__(*args, **kwargs, daemon=True)
        self._done = threading.Event()
        self._error_queue = queue.Queue()
        assert grain >= 0
        self._grain = grain

    def run(self):
        while not self._done.is_set():
            try:
                self._target(*self._args, **self._kwargs)
            except Exception as e:
                self._error_queue.put(e)
            time.sleep(self._grain)

    def kill(self):
        self._done.set()
        self.join()

    def process_errors(self):
        try:
            e = self._error_queue.get_nowait()
        except queue.Empty:
            return
        raise e


class Server(ServerBase):

    def __init__(self, grain: float = 0.0):
        super().__init__()
        self._daemon = Daemon(target=self._update, grain=grain)
        self._grain = grain

    def exec(self):
        self._daemon.start()

    def kill(self):
        self._daemon.kill()

    def process_errors(self):
        self._daemon.process_errors()
