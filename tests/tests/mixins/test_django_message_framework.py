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
