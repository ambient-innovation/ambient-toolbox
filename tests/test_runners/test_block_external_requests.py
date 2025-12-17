import socket
from unittest import TestCase, mock

from django.test import override_settings

from ambient_toolbox.tests.test_runners.block_external_requests import BlockingExternalRequestsRunner


class BlockingExternalRequestsRunnerTest(TestCase):
    def setUp(self):
        self.runner = BlockingExternalRequestsRunner()
        self.original_getaddrinfo = socket.getaddrinfo

    def tearDown(self):
        # Ensure socket.getaddrinfo is always restored
        socket.getaddrinfo = self.original_getaddrinfo
        # Clean up any patcher that might still be active
        if hasattr(self.runner, "_patcher") and self.runner._patcher:
            try:
                self.runner._patcher.stop()
            except RuntimeError:
                pass

    def test_allowed_hosts_constant(self):
        """Test that ALLOWED_HOSTS contains expected values."""
        expected_hosts = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}
        self.assertEqual(self.runner.ALLOWED_HOSTS, expected_hosts)

    def test_setup_and_teardown_full_cycle(self):
        """Test complete setup and teardown cycle with all functionality."""
        # Mock the parent class's methods to avoid Django global state issues
        with mock.patch.object(type(self.runner).__bases__[0], "setup_test_environment"):
            with mock.patch.object(type(self.runner).__bases__[0], "teardown_test_environment"):
                # Call setup_test_environment
                self.runner.setup_test_environment()

                # Verify original is stored
                self.assertEqual(self.runner._original_getaddrinfo, self.original_getaddrinfo)

                # Verify patcher exists and socket.getaddrinfo is patched
                self.assertTrue(hasattr(self.runner, "_patcher"))
                self.assertIsNotNone(self.runner._patcher)
                self.assertNotEqual(socket.getaddrinfo, self.original_getaddrinfo)

                # Test that all allowed hosts work
                for host in self.runner.ALLOWED_HOSTS:
                    result = socket.getaddrinfo(host, 80)
                    self.assertIsNotNone(result, f"Host {host} should be allowed")

                # Test that localhost works with additional arguments
                result = socket.getaddrinfo("localhost", 80, socket.AF_INET, socket.SOCK_STREAM)
                self.assertIsNotNone(result)

                # Verify external hosts are blocked
                with self.assertRaisesRegex(AssertionError, r"External request to 'example\.com' detected"):
                    socket.getaddrinfo("example.com", 80)

                # Verify external IPs are blocked
                with self.assertRaisesRegex(AssertionError, r"External request to '8\.8\.8\.8' detected"):
                    socket.getaddrinfo("8.8.8.8", 80)

                # Call teardown_test_environment
                self.runner.teardown_test_environment()

                # Verify socket.getaddrinfo is restored
                self.assertEqual(socket.getaddrinfo, self.original_getaddrinfo)

    def test_localhost_allowed_after_setup(self):
        """Test that localhost connections work after setup."""
        with mock.patch.object(type(self.runner).__bases__[0], "setup_test_environment"):
            with mock.patch.object(type(self.runner).__bases__[0], "teardown_test_environment"):
                self.runner.setup_test_environment()

                result = socket.getaddrinfo("localhost", 80)
                self.assertIsNotNone(result)

                self.runner.teardown_test_environment()

    def test_127_0_0_1_allowed_after_setup(self):
        """Test that 127.0.0.1 connections work after setup."""
        with mock.patch.object(type(self.runner).__bases__[0], "setup_test_environment"):
            with mock.patch.object(type(self.runner).__bases__[0], "teardown_test_environment"):
                self.runner.setup_test_environment()

                result = socket.getaddrinfo("127.0.0.1", 80)
                self.assertIsNotNone(result)

                self.runner.teardown_test_environment()

    def test_ipv6_localhost_allowed_after_setup(self):
        """Test that IPv6 localhost (::1) connections work after setup."""
        with mock.patch.object(type(self.runner).__bases__[0], "setup_test_environment"):
            with mock.patch.object(type(self.runner).__bases__[0], "teardown_test_environment"):
                self.runner.setup_test_environment()

                result = socket.getaddrinfo("::1", 80)
                self.assertIsNotNone(result)

                self.runner.teardown_test_environment()

    def test_0_0_0_0_allowed_after_setup(self):
        """Test that 0.0.0.0 connections work after setup."""
        with mock.patch.object(type(self.runner).__bases__[0], "setup_test_environment"):
            with mock.patch.object(type(self.runner).__bases__[0], "teardown_test_environment"):
                self.runner.setup_test_environment()

                result = socket.getaddrinfo("0.0.0.0", 80)
                self.assertIsNotNone(result)

                self.runner.teardown_test_environment()

    def test_external_host_blocked_after_setup(self):
        """Test that external host connections are blocked after setup."""
        with mock.patch.object(type(self.runner).__bases__[0], "setup_test_environment"):
            with mock.patch.object(type(self.runner).__bases__[0], "teardown_test_environment"):
                self.runner.setup_test_environment()

                with self.assertRaisesRegex(AssertionError, r"External request to 'example\.com' detected"):
                    socket.getaddrinfo("example.com", 80)

                self.runner.teardown_test_environment()

    def test_external_ip_blocked_after_setup(self):
        """Test that external IP connections are blocked after setup."""
        with mock.patch.object(type(self.runner).__bases__[0], "setup_test_environment"):
            with mock.patch.object(type(self.runner).__bases__[0], "teardown_test_environment"):
                self.runner.setup_test_environment()

                with self.assertRaisesRegex(AssertionError, r"External request to '8\.8\.8\.8' detected"):
                    socket.getaddrinfo("8.8.8.8", 80)

                self.runner.teardown_test_environment()

    def test_getaddrinfo_restored_after_teardown(self):
        """Test that socket.getaddrinfo is restored after teardown."""
        with mock.patch.object(type(self.runner).__bases__[0], "setup_test_environment"):
            with mock.patch.object(type(self.runner).__bases__[0], "teardown_test_environment"):
                self.runner.setup_test_environment()

                # Verify it's patched
                self.assertNotEqual(socket.getaddrinfo, self.original_getaddrinfo)

                self.runner.teardown_test_environment()

                # Verify it's restored
                self.assertEqual(socket.getaddrinfo, self.original_getaddrinfo)

    def test_getaddrinfo_handles_additional_arguments(self):
        """Test that patched getaddrinfo properly handles additional arguments."""
        with mock.patch.object(type(self.runner).__bases__[0], "setup_test_environment"):
            with mock.patch.object(type(self.runner).__bases__[0], "teardown_test_environment"):
                self.runner.setup_test_environment()

                result = socket.getaddrinfo("localhost", 80, socket.AF_INET, socket.SOCK_STREAM)
                self.assertIsNotNone(result)

                self.runner.teardown_test_environment()

    def test_handles_settings_not_configured(self):
        """Test that the runner works correctly when settings are not configured."""
        with mock.patch.object(type(self.runner).__bases__[0], "setup_test_environment"):
            with mock.patch.object(type(self.runner).__bases__[0], "teardown_test_environment"):
                # This should not raise an exception even if settings aren't fully configured
                self.runner.setup_test_environment()

                # Verify default hosts still work
                result = socket.getaddrinfo("localhost", 80)
                self.assertIsNotNone(result)

                # Verify external hosts are still blocked
                with self.assertRaisesRegex(AssertionError, r"External request to 'example\.com' detected"):
                    socket.getaddrinfo("example.com", 80)

                self.runner.teardown_test_environment()

    @override_settings(BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS=["example.test", "api.test"])
    def test_additional_hosts_from_django_settings(self):
        """Test that additional hosts from Django settings are allowed."""
        with mock.patch.object(type(self.runner).__bases__[0], "setup_test_environment"):
            with mock.patch.object(type(self.runner).__bases__[0], "teardown_test_environment"):
                self.runner.setup_test_environment()

                # Mock the underlying socket to return dummy data for test domains
                with mock.patch("socket._socket.getaddrinfo") as mock_gai:
                    mock_gai.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 80))]

                    # Verify default hosts still work
                    result = socket.getaddrinfo("localhost", 80)
                    self.assertIsNotNone(result)

                    # Verify additional hosts from settings are allowed
                    result = socket.getaddrinfo("example.test", 80)
                    self.assertIsNotNone(result)

                    result = socket.getaddrinfo("api.test", 80)
                    self.assertIsNotNone(result)

                # Verify other external hosts are still blocked
                with self.assertRaisesRegex(AssertionError, r"External request to 'example\.com' detected"):
                    socket.getaddrinfo("example.com", 80)

                self.runner.teardown_test_environment()

    @override_settings(BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS=["192.168.1.1", "10.0.0.1"])
    def test_additional_ip_addresses_from_django_settings(self):
        """Test that additional IP addresses from Django settings are allowed."""
        with mock.patch.object(type(self.runner).__bases__[0], "setup_test_environment"):
            with mock.patch.object(type(self.runner).__bases__[0], "teardown_test_environment"):
                self.runner.setup_test_environment()

                # Verify default hosts still work
                result = socket.getaddrinfo("localhost", 80)
                self.assertIsNotNone(result)

                # Verify additional IPs from settings are allowed
                result = socket.getaddrinfo("192.168.1.1", 80)
                self.assertIsNotNone(result)

                result = socket.getaddrinfo("10.0.0.1", 80)
                self.assertIsNotNone(result)

                # Verify other IPs are still blocked
                with self.assertRaisesRegex(AssertionError, r"External request to '8\.8\.8\.8' detected"):
                    socket.getaddrinfo("8.8.8.8", 80)

                self.runner.teardown_test_environment()

    @override_settings(BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS=[])
    def test_empty_additional_hosts_setting(self):
        """Test that empty additional hosts setting doesn't break functionality."""
        with mock.patch.object(type(self.runner).__bases__[0], "setup_test_environment"):
            with mock.patch.object(type(self.runner).__bases__[0], "teardown_test_environment"):
                self.runner.setup_test_environment()

                # Verify default hosts still work
                result = socket.getaddrinfo("localhost", 80)
                self.assertIsNotNone(result)

                # Verify external hosts are still blocked
                with self.assertRaisesRegex(AssertionError, r"External request to 'example\.com' detected"):
                    socket.getaddrinfo("example.com", 80)

                self.runner.teardown_test_environment()

    def test_exception_when_accessing_settings(self):
        """Test that the runner handles exceptions when accessing settings gracefully."""
        with mock.patch.object(type(self.runner).__bases__[0], "setup_test_environment"):
            with mock.patch.object(type(self.runner).__bases__[0], "teardown_test_environment"):
                # Mock getattr in the module to raise an exception when accessing the setting
                with mock.patch(
                    "ambient_toolbox.tests.test_runners.block_external_requests.getattr",
                    side_effect=lambda obj, name, default=None: (
                        (_ for _ in ()).throw(RuntimeError("Settings error"))
                        if name == "BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS"
                        else getattr(obj, name)
                        if default is None
                        else getattr(obj, name, default)
                    ),
                ):
                    # Should not raise - exception should be caught
                    self.runner.setup_test_environment()

                    # Verify default hosts still work
                    result = socket.getaddrinfo("localhost", 80)
                    self.assertIsNotNone(result)

                    # Verify external hosts are still blocked
                    with self.assertRaisesRegex(AssertionError, r"External request to 'example\.com' detected"):
                        socket.getaddrinfo("example.com", 80)

                    self.runner.teardown_test_environment()
