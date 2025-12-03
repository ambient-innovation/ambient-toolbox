import socket

import pytest


class TestBlockExternalRequestsFixture:
    """Tests for the block_external_requests pytest fixture."""

    def test_fixture_allows_localhost(self, block_external_requests):
        """Test that the fixture allows connections to 'localhost'."""
        result = socket.getaddrinfo("localhost", 80)
        assert result is not None

    def test_fixture_allows_127_0_0_1(self, block_external_requests):
        """Test that the fixture allows connections to '127.0.0.1'."""
        result = socket.getaddrinfo("127.0.0.1", 80)
        assert result is not None

    def test_fixture_allows_ipv6_localhost(self, block_external_requests):
        """Test that the fixture allows connections to IPv6 localhost '::1'."""
        result = socket.getaddrinfo("::1", 80)
        assert result is not None

    def test_fixture_allows_0_0_0_0(self, block_external_requests):
        """Test that the fixture allows connections to '0.0.0.0'."""
        result = socket.getaddrinfo("0.0.0.0", 80)
        assert result is not None

    def test_fixture_blocks_external_domain(self, block_external_requests):
        """Test that the fixture blocks connections to external domains."""
        with pytest.raises(AssertionError) as exc_info:
            socket.getaddrinfo("example.com", 80)

        assert "External request to example.com detected" in str(exc_info.value)

    def test_fixture_blocks_external_ip(self, block_external_requests):
        """Test that the fixture blocks connections to external IP addresses."""
        with pytest.raises(AssertionError) as exc_info:
            socket.getaddrinfo("8.8.8.8", 80)

        assert "External request to 8.8.8.8 detected" in str(exc_info.value)

    def test_fixture_blocks_google_dns(self, block_external_requests):
        """Test that the fixture blocks connections to google.com."""
        with pytest.raises(AssertionError) as exc_info:
            socket.getaddrinfo("google.com", 443)

        assert "External request to google.com detected" in str(exc_info.value)

    def test_fixture_handles_additional_args(self, block_external_requests):
        """Test that the fixture handles additional arguments to getaddrinfo."""
        result = socket.getaddrinfo("localhost", 80, socket.AF_INET, socket.SOCK_STREAM)
        assert result is not None

    def test_fixture_handles_kwargs(self, block_external_requests):
        """Test that the fixture handles keyword arguments to getaddrinfo."""
        result = socket.getaddrinfo("localhost", 80, family=socket.AF_INET, type=socket.SOCK_STREAM)
        assert result is not None

    def test_all_allowed_hosts(self, block_external_requests):
        """Test that all expected hosts are allowed."""
        expected_hosts = ["localhost", "127.0.0.1", "::1", "0.0.0.0"]
        for host in expected_hosts:
            result = socket.getaddrinfo(host, 80)
            assert result is not None

    def test_various_blocked_hosts(self, block_external_requests):
        """Test that various external hosts are blocked."""
        blocked_hosts = ["192.168.1.1", "10.0.0.1", "172.16.0.1", "example.com"]
        for host in blocked_hosts:
            with pytest.raises(AssertionError) as exc_info:
                socket.getaddrinfo(host, 80)
            assert f"External request to {host} detected" in str(exc_info.value)

    def test_fixture_with_different_ports(self, block_external_requests):
        """Test that the fixture works correctly with different port numbers."""
        for port in [80, 443, 8000, 8080, 5432, 3306]:
            result = socket.getaddrinfo("localhost", port)
            assert result is not None

    def test_fixture_blocks_private_network_ips(self, block_external_requests):
        """Test that the fixture blocks private network IP addresses."""
        private_ips = ["192.168.1.1", "10.0.0.1", "172.16.0.1"]
        for ip in private_ips:
            with pytest.raises(AssertionError) as exc_info:
                socket.getaddrinfo(ip, 80)
            assert f"External request to {ip} detected" in str(exc_info.value)
