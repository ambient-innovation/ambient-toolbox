from django.contrib import messages
from django.test import TestCase

from ambient_toolbox.tests.mixins import DjangoMessagingFrameworkTestMixin, RequestProviderMixin


class DjangoMessagingFrameworkTestMixinTest(RequestProviderMixin, DjangoMessagingFrameworkTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.request = cls.get_request()

    def test_full_message_found(self):
        messages.add_message(self.request, messages.INFO, "My message")
        self.assert_full_message_in_request(request=self.request, message="My message")

    def test_partial_message_found(self):
        messages.add_message(self.request, messages.INFO, "My message")
        self.assert_partial_message_in_request(request=self.request, message="My")

    def test_message_not_found(self):
        messages.add_message(self.request, messages.INFO, "My message")
        self.assert_message_not_in_request(request=self.request, message="Ninja")

    def test_message_not_found_but_found(self):
        messages.add_message(self.request, messages.INFO, "My message")
        with self.assertRaises(AssertionError):
            self.assert_message_not_in_request(request=self.request, message="My message")

    def test_full_message_no_messages_in_request(self):
        # Test assert_full_message_in_request when request has no messages
        empty_request = self.get_request()
        with self.assertRaises(AssertionError) as context:
            self.assert_full_message_in_request(request=empty_request, message="My message")
        self.assertIn("doesn't contain any messages", str(context.exception))

    def test_full_message_not_found_in_request(self):
        # Test assert_full_message_in_request when message is not found
        messages.add_message(self.request, messages.INFO, "Different message")
        with self.assertRaises(AssertionError) as context:
            self.assert_full_message_in_request(request=self.request, message="My message")
        self.assertIn("not found in request", str(context.exception))

    def test_partial_message_no_messages_in_request(self):
        # Test assert_partial_message_in_request when request has no messages
        empty_request = self.get_request()
        with self.assertRaises(AssertionError) as context:
            self.assert_partial_message_in_request(request=empty_request, message="My")
        self.assertIn("doesn't contain any messages", str(context.exception))

    def test_partial_message_not_found_in_request(self):
        # Test assert_partial_message_in_request when message part is not found
        messages.add_message(self.request, messages.INFO, "Different message")
        with self.assertRaises(AssertionError) as context:
            self.assert_partial_message_in_request(request=self.request, message="Ninja")
        self.assertIn("not found in request", str(context.exception))

    def test_message_not_in_request_with_no_messages(self):
        # Test assert_message_not_in_request when request has no messages (should pass)
        empty_request = self.get_request()
        # This should not raise an error
        self.assert_message_not_in_request(request=empty_request, message="Any message")

    def test_multiple_messages_full_match(self):
        # Test with multiple messages to ensure loop coverage
        messages.add_message(self.request, messages.INFO, "First message")
        messages.add_message(self.request, messages.WARNING, "Second message")
        messages.add_message(self.request, messages.ERROR, "Third message")
        self.assert_full_message_in_request(request=self.request, message="Second message")

    def test_multiple_messages_partial_match(self):
        # Test with multiple messages to ensure loop coverage
        messages.add_message(self.request, messages.INFO, "First message")
        messages.add_message(self.request, messages.WARNING, "Second message")
        messages.add_message(self.request, messages.ERROR, "Third message")
        self.assert_partial_message_in_request(request=self.request, message="Second")

    def test_multiple_messages_not_in_request(self):
        # Test with multiple messages to ensure loop coverage
        messages.add_message(self.request, messages.INFO, "First message")
        messages.add_message(self.request, messages.WARNING, "Second message")
        messages.add_message(self.request, messages.ERROR, "Third message")
        self.assert_message_not_in_request(request=self.request, message="Fourth message")
