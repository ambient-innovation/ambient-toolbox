import socket
from unittest import mock

from django.test.runner import DiscoverRunner


class BlockingExternalRequestsRunner(DiscoverRunner):
    """
    Ensures that tests don't talk to the internet by accident.
    """

    ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}

    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        self._original_getaddrinfo = socket.getaddrinfo

        def assert_only_localhost(host, *args, **kwargs):
            assert host in self.ALLOWED_HOSTS, f"External request to {host!r} detected."
            return self._original_getaddrinfo(host, *args, **kwargs)

        self._patcher = mock.patch("socket.getaddrinfo", side_effect=assert_only_localhost)
        self._patcher.start()

    def teardown_test_environment(self, **kwargs):
        self._patcher.stop()
        super().teardown_test_environment(**kwargs)
