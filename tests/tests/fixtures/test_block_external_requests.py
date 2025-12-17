import socket
from unittest import mock

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


class TestBlockExternalRequestsFixtureWithDjangoSettings:
    """Tests for the block_external_requests fixture with Django settings configured."""

    @pytest.fixture(autouse=True)
    def setup_settings(self, settings, monkeypatch):
        """Set up Django settings and mock getaddrinfo for test domains."""
        settings.BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS = ["example.test", "api.test"]

        # Store the original getaddrinfo before any patching
        original_getaddrinfo = (
            socket.getaddrinfo.__wrapped__ if hasattr(socket.getaddrinfo, "__wrapped__") else socket._socket.getaddrinfo
        )

        def mock_getaddrinfo(host, port, *args, **kwargs):
            # Return dummy data for test domains
            if host in ["example.test", "api.test"]:
                return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", port))]
            return original_getaddrinfo(host, port, *args, **kwargs)

        monkeypatch.setattr(socket, "_original_getaddrinfo", mock_getaddrinfo, raising=False)

    def test_fixture_allows_additional_hosts_from_settings(self, block_external_requests):
        """Test that additional hosts from Django settings are allowed."""
        # Mock the underlying getaddrinfo to return dummy data
        with mock.patch("socket._socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 80))]

            # Verify default hosts still work
            result = socket.getaddrinfo("localhost", 80)
            assert result is not None

            # Verify additional hosts from settings are allowed
            result = socket.getaddrinfo("example.test", 80)
            assert result is not None

            result = socket.getaddrinfo("api.test", 80)
            assert result is not None

        # Verify other external hosts are still blocked
        with pytest.raises(AssertionError) as exc_info:
            socket.getaddrinfo("example.com", 80)
        assert "External request to example.com detected" in str(exc_info.value)

    def test_fixture_with_additional_settings_and_ports(self, block_external_requests):
        """Test that additional hosts work with different ports."""
        with mock.patch("socket._socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 80))]

            for port in [80, 443, 8000, 8080]:
                result = socket.getaddrinfo("example.test", port)
                assert result is not None

    def test_fixture_still_blocks_unlisted_hosts(self, block_external_requests):
        """Test that hosts not in settings are still blocked."""
        blocked_hosts = ["google.com", "github.com", "8.8.8.8"]
        for host in blocked_hosts:
            with pytest.raises(AssertionError) as exc_info:
                socket.getaddrinfo(host, 80)
            assert f"External request to {host} detected" in str(exc_info.value)


class TestBlockExternalRequestsFixtureWithIPAddressSettings:
    """Tests for the fixture with IP address settings."""

    @pytest.fixture(autouse=True)
    def setup_settings(self, settings):
        """Set up Django settings before the test runs."""
        settings.BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS = ["192.168.1.100", "10.0.0.50"]

    def test_fixture_allows_ip_addresses_from_settings(self, block_external_requests):
        """Test that IP addresses from Django settings are allowed."""
        # Mock the underlying getaddrinfo to return dummy data
        with mock.patch("socket._socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.1.100", 80))]

            # Verify additional IPs from settings are allowed
            result = socket.getaddrinfo("192.168.1.100", 80)
            assert result is not None

            mock_gai.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.50", 80))]
            result = socket.getaddrinfo("10.0.0.50", 80)
            assert result is not None

        # Verify other IPs are still blocked
        with pytest.raises(AssertionError) as exc_info:
            socket.getaddrinfo("8.8.8.8", 80)
        assert "External request to 8.8.8.8 detected" in str(exc_info.value)


class TestBlockExternalRequestsFixtureWithEmptySettings:
    """Tests for the fixture with empty settings list."""

    @pytest.fixture(autouse=True)
    def setup_settings(self, settings):
        """Set up Django settings before the test runs."""
        settings.BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS = []

    def test_fixture_with_empty_settings_list(self, block_external_requests):
        """Test that empty settings list doesn't break functionality."""
        # Verify default hosts still work
        result = socket.getaddrinfo("localhost", 80)
        assert result is not None

        # Verify external hosts are still blocked
        with pytest.raises(AssertionError) as exc_info:
            socket.getaddrinfo("example.com", 80)
        assert "External request to example.com detected" in str(exc_info.value)


class TestBlockExternalRequestsFixtureWithAdditionalHosts:
    """Tests for the fixture when Django settings provide additional allowed hosts."""

    @pytest.fixture(autouse=True)
    def setup_additional_hosts(self):
        """Set up environment where Django settings provide additional hosts."""
        from django.conf import settings as real_settings  # noqa: PLC0415

        # Create a wrapper that returns additional hosts
        class MockSettingsWrapper:
            BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS = ["test.example.com", "api.example.com"]

            def __getattr__(self, name):
                if name == "BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS":
                    return self.BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS
                return getattr(real_settings, name)

        # Patch settings before the fixture runs
        with mock.patch("django.conf.settings", MockSettingsWrapper()):
            yield

    def test_fixture_with_additional_hosts_from_settings(self, block_external_requests):
        """Test that the fixture allows additional hosts from Django settings."""
        # Verify default hosts still work
        result = socket.getaddrinfo("localhost", 80)
        assert result is not None

        # Mock the underlying socket to return dummy data for test domains
        with mock.patch("socket._socket.getaddrinfo") as mock_gai:
            mock_gai.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 80))]

            # Verify additional hosts from settings are allowed
            result = socket.getaddrinfo("test.example.com", 80)
            assert result is not None

            result = socket.getaddrinfo("api.example.com", 80)
            assert result is not None

        # Verify other external hosts are still blocked
        with pytest.raises(AssertionError) as exc_info:
            socket.getaddrinfo("google.com", 80)
        assert "External request to google.com detected" in str(exc_info.value)


class TestBlockExternalRequestsFixtureWithNoneSettings:
    """Tests for the fixture when Django settings return None for additional hosts."""

    @pytest.fixture(autouse=True)
    def setup_none_settings(self):
        """Set up environment where Django settings return None."""
        from django.conf import settings as real_settings  # noqa: PLC0415

        # Create a wrapper that returns None for the setting
        class MockSettingsWrapper:
            BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS = None

            def __getattr__(self, name):
                if name == "BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS":
                    return self.BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS
                return getattr(real_settings, name)

        # Patch settings before the fixture runs
        with mock.patch("django.conf.settings", MockSettingsWrapper()):
            yield

    def test_fixture_with_none_additional_hosts(self, block_external_requests):
        """Test that the fixture handles None additional hosts correctly."""
        # Verify default hosts still work
        result = socket.getaddrinfo("localhost", 80)
        assert result is not None

        # Verify external hosts are still blocked
        with pytest.raises(AssertionError) as exc_info:
            socket.getaddrinfo("example.com", 80)
        assert "External request to example.com detected" in str(exc_info.value)


class TestBlockExternalRequestsFixtureWithImproperlyConfigured:
    """Tests for the fixture when Django settings raise ImproperlyConfigured."""

    @pytest.fixture(autouse=True)
    def setup_improperly_configured(self):
        """Set up environment where Django settings raise ImproperlyConfigured."""
        from django.conf import settings as real_settings  # noqa: PLC0415
        from django.core.exceptions import ImproperlyConfigured  # noqa: PLC0415

        # Create a wrapper that raises ImproperlyConfigured
        class MockSettingsWrapper:
            def __getattr__(self, name):
                if name == "BLOCKING_EXTERNAL_REQUESTS_ALLOWED_HOSTS":
                    raise ImproperlyConfigured("Settings are not configured properly")
                return getattr(real_settings, name)

        # Patch settings before the fixture runs
        with mock.patch("django.conf.settings", MockSettingsWrapper()):
            yield

    def test_fixture_handles_improperly_configured_exception(self, block_external_requests):
        """Test that the fixture gracefully handles ImproperlyConfigured exception."""
        # Verify default hosts still work (fixture should fall back to defaults)
        result = socket.getaddrinfo("localhost", 80)
        assert result is not None

        # Verify external hosts are still blocked
        with pytest.raises(AssertionError) as exc_info:
            socket.getaddrinfo("example.com", 80)
        assert "External request to example.com detected" in str(exc_info.value)


class TestBlockExternalRequestsFixtureWithoutDjango:
    """Tests for the fixture when Django is not available."""

    @pytest.fixture(autouse=True)
    def setup_no_django(self):
        """Set up environment where Django is not available."""
        original_import = __import__

        def mock_import(name, *args, **kwargs):
            if name in ("django.conf", "django.core.exceptions"):
                raise ImportError(f"No module named '{name}'")
            return original_import(name, *args, **kwargs)

        # Patch imports before the fixture runs
        with mock.patch("builtins.__import__", side_effect=mock_import):
            # Reload the fixture module
            from importlib import reload  # noqa: PLC0415

            import ambient_toolbox.tests.fixtures.block_external_requests as fixture_module  # noqa: PLC0415

            reload(fixture_module)
            yield
            # Reload again to restore
            reload(fixture_module)

    def test_fixture_handles_django_import_error(self, block_external_requests):
        """Test that the fixture gracefully handles ImportError when Django is not available."""
        # Verify default hosts still work (fixture should fall back to defaults)
        result = socket.getaddrinfo("localhost", 80)
        assert result is not None

        # Verify external hosts are still blocked
        with pytest.raises(AssertionError) as exc_info:
            socket.getaddrinfo("example.com", 80)
        assert "External request to example.com detected" in str(exc_info.value)
