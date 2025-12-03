import socket
from unittest import TestCase, mock

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
