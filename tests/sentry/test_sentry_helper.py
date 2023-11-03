import copy

from django.test import TestCase

from ambient_toolbox.sentry.helpers import SentryEventScrubber, strip_sensitive_data_from_sentry_event
from tests.sentry.mock_data import SCRUBBED_SENTRY_EVENT, SENTRY_EVENT


class SentryHelperTest(TestCase):
    def test_strip_sensitive_data_from_sentry_event_regular(self):
        event = {"user": {"email": "mymail@example.com", "ip_address": "127.0.0.1", "username": "my-user"}}

        self.assertIsInstance(strip_sensitive_data_from_sentry_event(event, None), dict)

    def test_strip_sensitive_data_from_sentry_event_missing_key_email(self):
        event = {"user": {"ip_address": "127.0.0.1", "username": "my-user"}}

        self.assertIsInstance(strip_sensitive_data_from_sentry_event(event, None), dict)

    def test_strip_sensitive_data_from_sentry_event_missing_key_ip_address(self):
        event = {"user": {"email": "mymail@example.com", "username": "my-user"}}

        self.assertIsInstance(strip_sensitive_data_from_sentry_event(event, None), dict)

    def test_strip_sensitive_data_from_sentry_event_missing_key_username(self):
        event = {"user": {"email": "mymail@example.com", "ip_address": "127.0.0.1"}}

        self.assertIsInstance(strip_sensitive_data_from_sentry_event(event, None), dict)

    def test_sentry_event_scrubber_on_a_regular_sentry_event(self):
        event = copy.deepcopy(SENTRY_EVENT)
        self.assertEqual(
            SCRUBBED_SENTRY_EVENT,
            SentryEventScrubber().scrub_sensitive_data_from_sentry_event(event, None),
        )
