from django.test import TestCase

from ambient_toolbox.sentry.helpers import strip_sensitive_data_from_sentry_event


class SentryHelperTest(TestCase):
    def test_strip_sensitive_data_from_sentry_event_regular(self):
        event = {"user": {"email": "mymail@example.com", "ip_address": "127.0.0.1", "username": "my-user"}}

        self.assertIsInstance(strip_sensitive_data_from_sentry_event(event, None), dict)

    def test_strip_sensitive_data_from_sentry_event_missing_key_email(self):
        event = {"user": {"ip_address": "127.0.0.1", "username": "my-user"}}

        self.assertIsInstance(strip_sensitive_data_from_sentry_event(event, None), dict)

    def test_strip_sensitive_data_from_sentry_event_missing_key_ip_address(self):
        event = {"user": {"email": "mymail@example.com", "username": "my-user"}}

        stripped_event = strip_sensitive_data_from_sentry_event(event, None)

        self.assertIsInstance(stripped_event, dict)
        self.assertNotIn("email", stripped_event["user"].keys())
        self.assertNotIn("username", stripped_event["user"].keys())

    def test_strip_sensitive_data_from_sentry_event_missing_key_username(self):
        event = {"user": {"email": "mymail@example.com", "ip_address": "127.0.0.1"}}

        stripped_event = strip_sensitive_data_from_sentry_event(event, None)

        self.assertIsInstance(stripped_event, dict)
        self.assertNotIn("email", stripped_event["user"].keys())
        self.assertNotIn("ip_address", stripped_event["user"].keys())
