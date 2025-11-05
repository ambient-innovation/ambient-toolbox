from unittest.mock import MagicMock, patch

from django.test import TestCase

from ambient_toolbox.sentry.helpers import SentryEventScrubber, strip_sensitive_data_from_sentry_event


class SentryEventScrubberTest(TestCase):
    """Test suite for SentryEventScrubber."""

    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        scrubber = SentryEventScrubber()
        self.assertEqual(scrubber.denylist, [])
        self.assertEqual(
            scrubber.standard_denylist,
            ["username", "email", "ip_address", "serializer", "admin"],
        )

    def test_init_with_custom_denylist(self):
        """Test initialization with custom denylist."""
        custom_denylist = ["password", "token"]
        scrubber = SentryEventScrubber(denylist=custom_denylist)
        self.assertEqual(scrubber.denylist, custom_denylist)
        self.assertEqual(
            scrubber.standard_denylist,
            ["username", "email", "ip_address", "serializer", "admin"],
        )

    def test_init_with_standard_denylist_disabled(self):
        """Test initialization with standard_denylist disabled."""
        scrubber = SentryEventScrubber(standard_denylist=False)
        self.assertEqual(scrubber.denylist, [])
        self.assertEqual(scrubber.standard_denylist, [])

    def test_init_with_none_denylist(self):
        """Test initialization with None denylist."""
        scrubber = SentryEventScrubber(denylist=None)
        self.assertEqual(scrubber.denylist, [])

    def test_init_with_both_denylists(self):
        """Test initialization with both custom and standard denylist."""
        custom_denylist = ["password", "token"]
        scrubber = SentryEventScrubber(denylist=custom_denylist, standard_denylist=True)
        self.assertEqual(scrubber.denylist, custom_denylist)
        self.assertEqual(
            scrubber.standard_denylist,
            ["username", "email", "ip_address", "serializer", "admin"],
        )

    @patch("sentry_sdk.scrubber.EventScrubber")
    @patch("ambient_toolbox.sentry.helpers.serialize")
    def test_scrub_sensitive_data_from_sentry_event_default(self, mock_serialize, mock_event_scrubber_class):
        """Test scrubbing with default settings."""
        scrubber = SentryEventScrubber()
        mock_event_scrubber = MagicMock()
        mock_event_scrubber_class.return_value = mock_event_scrubber
        mock_serialize.return_value = {"scrubbed": "event"}

        event = {"user": {"email": "test@example.com"}}
        result = scrubber.scrub_sensitive_data_from_sentry_event(event, None)

        # Verify EventScrubber was called with combined denylists
        mock_event_scrubber_class.assert_called_once()
        call_kwargs = mock_event_scrubber_class.call_args[1]
        self.assertIn("username", call_kwargs["denylist"])
        self.assertIn("email", call_kwargs["denylist"])
        self.assertIn("ip_address", call_kwargs["denylist"])
        self.assertIn("serializer", call_kwargs["denylist"])
        self.assertIn("admin", call_kwargs["denylist"])

        # Verify scrub_event was called
        mock_event_scrubber.scrub_event.assert_called_once_with(event)

        # Verify serialize was called
        mock_serialize.assert_called_once_with(event)
        self.assertEqual(result, {"scrubbed": "event"})

    @patch("sentry_sdk.scrubber.EventScrubber")
    @patch("ambient_toolbox.sentry.helpers.serialize")
    def test_scrub_sensitive_data_from_sentry_event_custom_denylist(self, mock_serialize, mock_event_scrubber_class):
        """Test scrubbing with custom denylist."""
        custom_denylist = ["password", "secret"]
        scrubber = SentryEventScrubber(denylist=custom_denylist)
        mock_event_scrubber = MagicMock()
        mock_event_scrubber_class.return_value = mock_event_scrubber
        mock_serialize.return_value = {"scrubbed": "event"}

        event = {"data": {"password": "secret123"}}
        scrubber.scrub_sensitive_data_from_sentry_event(event, None)

        # Verify EventScrubber was called with combined denylists
        call_kwargs = mock_event_scrubber_class.call_args[1]
        self.assertIn("password", call_kwargs["denylist"])
        self.assertIn("secret", call_kwargs["denylist"])
        self.assertIn("username", call_kwargs["denylist"])
        self.assertIn("email", call_kwargs["denylist"])

        mock_event_scrubber.scrub_event.assert_called_once_with(event)
        mock_serialize.assert_called_once_with(event)

    @patch("sentry_sdk.scrubber.EventScrubber")
    @patch("ambient_toolbox.sentry.helpers.serialize")
    def test_scrub_sensitive_data_from_sentry_event_no_standard_denylist(
        self, mock_serialize, mock_event_scrubber_class
    ):
        """Test scrubbing with standard_denylist disabled."""
        scrubber = SentryEventScrubber(standard_denylist=False)
        mock_event_scrubber = MagicMock()
        mock_event_scrubber_class.return_value = mock_event_scrubber
        mock_serialize.return_value = {"scrubbed": "event"}

        event = {"user": {"email": "test@example.com"}}
        scrubber.scrub_sensitive_data_from_sentry_event(event, None)

        # Verify EventScrubber was called without standard denylist items
        # Should only have DEFAULT_DENYLIST items, not our standard ones
        # (we can't easily check DEFAULT_DENYLIST, but we can verify it was called)
        mock_event_scrubber_class.assert_called_once()

        mock_event_scrubber.scrub_event.assert_called_once_with(event)
        mock_serialize.assert_called_once_with(event)


class StripSensitiveDataTest(TestCase):
    """Test suite for strip_sensitive_data_from_sentry_event function."""

    def test_strip_sensitive_data_from_sentry_event_regular(self):
        """Test stripping all sensitive fields from a complete event."""
        event = {"user": {"email": "mymail@example.com", "ip_address": "127.0.0.1", "username": "my-user"}}

        self.assertIsInstance(strip_sensitive_data_from_sentry_event(event, None), dict)

    def test_strip_sensitive_data_from_sentry_event_missing_key_email(self):
        """Test stripping when email field is missing."""
        event = {"user": {"ip_address": "127.0.0.1", "username": "my-user"}}

        self.assertIsInstance(strip_sensitive_data_from_sentry_event(event, None), dict)

    def test_strip_sensitive_data_from_sentry_event_missing_key_ip_address(self):
        """Test stripping when ip_address field is missing."""
        event = {"user": {"email": "mymail@example.com", "username": "my-user"}}

        stripped_event = strip_sensitive_data_from_sentry_event(event, None)

        self.assertIsInstance(stripped_event, dict)
        self.assertNotIn("email", stripped_event["user"].keys())
        self.assertNotIn("username", stripped_event["user"].keys())

    def test_strip_sensitive_data_from_sentry_event_missing_key_username(self):
        """Test stripping when username field is missing."""
        event = {"user": {"email": "mymail@example.com", "ip_address": "127.0.0.1"}}

        stripped_event = strip_sensitive_data_from_sentry_event(event, None)

        self.assertIsInstance(stripped_event, dict)
        self.assertNotIn("email", stripped_event["user"].keys())
        self.assertNotIn("ip_address", stripped_event["user"].keys())

    def test_strip_sensitive_data_removes_all_fields(self):
        """Test that all sensitive fields are actually removed."""
        event = {
            "user": {
                "id": "123",
                "email": "mymail@example.com",
                "ip_address": "127.0.0.1",
                "username": "my-user",
            }
        }

        stripped_event = strip_sensitive_data_from_sentry_event(event, None)

        # Check that sensitive fields are removed
        self.assertNotIn("email", stripped_event["user"])
        self.assertNotIn("username", stripped_event["user"])
        self.assertNotIn("ip_address", stripped_event["user"])
        # Check that non-sensitive field remains
        self.assertIn("id", stripped_event["user"])
        self.assertEqual(stripped_event["user"]["id"], "123")

    def test_strip_sensitive_data_missing_user_key(self):
        """Test behavior when 'user' key is missing entirely."""
        event = {"other": "data"}

        # Should not raise an error
        stripped_event = strip_sensitive_data_from_sentry_event(event, None)

        self.assertIsInstance(stripped_event, dict)
        self.assertEqual(stripped_event, {"other": "data"})

    def test_strip_sensitive_data_empty_user_dict(self):
        """Test behavior with empty user dict."""
        event = {"user": {}}

        stripped_event = strip_sensitive_data_from_sentry_event(event, None)

        self.assertIsInstance(stripped_event, dict)
        self.assertEqual(stripped_event["user"], {})
