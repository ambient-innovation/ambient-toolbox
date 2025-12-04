import socket

import pytest


@pytest.fixture
def block_external_requests(monkeypatch):
    """
    Blocks external network requests during tests, allowing only localhost connections.

    Additional hosts can be allowed by setting the Django setting
    BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS to a list or set of hostnames/IPs.

    Source: https://blog.pecar.me/disable-network-requets-when-running-pytest
    """
    original_getaddrinfo = socket.getaddrinfo
    allowed_hosts = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}

    # Try to get additional allowed hosts from Django settings if available
    try:
        from django.conf import settings  # noqa: PLC0415
        from django.core.exceptions import ImproperlyConfigured  # noqa: PLC0415

        try:
            additional_hosts = getattr(settings, "BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS", None)
            if additional_hosts:
                allowed_hosts = allowed_hosts.copy()
                allowed_hosts.update(additional_hosts)
        except ImproperlyConfigured:
            # Django settings not configured, use default hosts only
            pass
    except ImportError:
        # Django not available, use default hosts only
        pass

    def assert_only_localhost(host, *args, **kwargs):
        assert host in allowed_hosts, f"External request to {host} detected"
        return original_getaddrinfo(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", assert_only_localhost)
