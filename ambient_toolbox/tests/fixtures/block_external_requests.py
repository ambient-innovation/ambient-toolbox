import socket

import pytest


@pytest.fixture
def block_external_requests(monkeypatch):
    """
    Source: https://blog.pecar.me/disable-network-requets-when-running-pytest
    """
    original_getaddrinfo = socket.getaddrinfo
    allowed_hosts = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}

    def assert_only_localhost(host, *args, **kwargs):
        assert host in allowed_hosts, f"External request to {host} detected"
        return original_getaddrinfo(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", assert_only_localhost)
