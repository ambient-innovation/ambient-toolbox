import socket
from unittest import mock

from django.conf import settings
from django.test.runner import DiscoverRunner


class BlockingExternalRequestsRunner(DiscoverRunner):
    """
    Ensures that tests don't talk to the internet by accident.

    Additional hosts can be allowed by setting the Django setting
    BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS to a list or set of hostnames/IPs.
    """

    ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}

    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        self._original_getaddrinfo = socket.getaddrinfo

        # Merge default allowed hosts with additional hosts from settings
        allowed_hosts = self.ALLOWED_HOSTS.copy()
        try:
            additional_hosts = getattr(settings, "BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS", None)
            if additional_hosts:
                allowed_hosts.update(additional_hosts)
        except Exception:  # noqa: BLE001
            # Settings might not be fully configured during test setup
            # This is OK, we'll just use the default allowed hosts
            pass

        def assert_only_localhost(host, *args, **kwargs):
            assert host in allowed_hosts, f"External request to {host!r} detected."
            return self._original_getaddrinfo(host, *args, **kwargs)

        self._patcher = mock.patch("socket.getaddrinfo", side_effect=assert_only_localhost)
        self._patcher.start()

    def teardown_test_environment(self, **kwargs):
        self._patcher.stop()
        super().teardown_test_environment(**kwargs)
