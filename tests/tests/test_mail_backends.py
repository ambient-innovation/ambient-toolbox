from unittest import mock

from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.test import TestCase, override_settings

from ambient_toolbox.mail.backends.whitelist_smtp import WhitelistEmailBackend


@override_settings(
    EMAIL_BACKEND="ambient_toolbox.mail.backends.whitelist_smtp.WhitelistEmailBackend",
    EMAIL_BACKEND_DOMAIN_WHITELIST=["valid.domain"],
    EMAIL_BACKEND_REDIRECT_ADDRESS="%s@testuser.valid.domain",
)
class MailBackendWhitelistBackendTest(TestCase):
    def test_whitify_mail_addresses_replace(self):
        email_1 = "albertus.magnus@example.com"
        email_2 = "thomas_von_aquin@example.com"
        processed_list = WhitelistEmailBackend.whitify_mail_addresses(mail_address_list=[email_1, email_2])

        self.assertEqual(len(processed_list), 2)
        self.assertEqual(processed_list[0], "albertus.magnus_example.com@testuser.valid.domain")
        self.assertEqual(processed_list[1], "thomas_von_aquin_example.com@testuser.valid.domain")

    def test_whitify_mail_addresses_whitelisted_domain(self):
        email = "platon@valid.domain"
        processed_list = WhitelistEmailBackend.whitify_mail_addresses(mail_address_list=[email])

        self.assertEqual(len(processed_list), 1)
        self.assertEqual(processed_list[0], email)

    @override_settings(EMAIL_BACKEND_REDIRECT_ADDRESS="")
    def test_whitify_mail_addresses_no_redirect_configured(self):
        email = "sokrates@example.com"
        processed_list = WhitelistEmailBackend.whitify_mail_addresses(mail_address_list=[email])

        self.assertEqual(len(processed_list), 0)

    def test_process_recipients_regular(self):
        mail = EmailMultiAlternatives(
            "Test subject", "Here is the message.", "from@example.com", ["to@example.com"], connection=None
        )

        backend = WhitelistEmailBackend()
        message_list = backend._process_recipients([mail])
        self.assertEqual(len(message_list), 1)
        self.assertEqual(message_list[0].to, ["to_example.com@testuser.valid.domain"])

    @mock.patch.object(EmailBackend, "send_messages")
    @mock.patch.object(WhitelistEmailBackend, "_process_recipients")
    def test_send_messages_process_recipients_called(self, mocked_process_recipients, *args):
        backend = WhitelistEmailBackend()
        backend.send_messages([])

        mocked_process_recipients.assert_called_once_with([])

    @mock.patch.object(EmailBackend, "send_messages")
    def test_send_messages_super_called(self, mocked_send_messages):
        backend = WhitelistEmailBackend()
        backend.send_messages([])

        mocked_send_messages.assert_called_once_with([])
