from unittest import mock

from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.test import TestCase, override_settings

from ambient_toolbox.mail.backends.allowlist_smtp import AllowlistEmailBackend
from ambient_toolbox.mail.backends.whitelist_smtp import WhitelistEmailBackend


@override_settings(
    EMAIL_BACKEND_DOMAIN_ALLOWLIST=["valid.domain"],
    EMAIL_BACKEND_REDIRECT_ADDRESS="%s@testuser.valid.domain",
)
class MailBackendAllowlistBackendTest(TestCase):
    def test_allowlist_mail_addresses_replace(self):
        email_1 = "albertus.magnus@example.com"
        email_2 = "thomas_von_aquin@example.com"
        processed_list = AllowlistEmailBackend.allowlist_mail_addresses(mail_address_list=[email_1, email_2])

        self.assertEqual(len(processed_list), 2)
        self.assertEqual(processed_list[0], "albertus.magnus_example.com@testuser.valid.domain")
        self.assertEqual(processed_list[1], "thomas_von_aquin_example.com@testuser.valid.domain")

    def test_allowlist_mail_addresses_whitelisted_domain(self):
        email = "platon@valid.domain"
        processed_list = AllowlistEmailBackend.allowlist_mail_addresses(mail_address_list=[email])

        self.assertEqual(len(processed_list), 1)
        self.assertEqual(processed_list[0], email)

    @override_settings(EMAIL_BACKEND_REDIRECT_ADDRESS="")
    def test_allowlist_mail_addresses_no_redirect_configured(self):
        email = "sokrates@example.com"
        processed_list = AllowlistEmailBackend.allowlist_mail_addresses(mail_address_list=[email])

        self.assertEqual(len(processed_list), 0)

    def test_process_recipients_regular(self):
        mail = EmailMultiAlternatives(
            "Test subject", "Here is the message.", "from@example.com", ["to@example.com"], connection=None
        )

        backend = AllowlistEmailBackend()
        message_list = backend._process_recipients([mail])
        self.assertEqual(len(message_list), 1)
        self.assertEqual(message_list[0].to, ["to_example.com@testuser.valid.domain"])

    @mock.patch.object(EmailBackend, "send_messages")
    @mock.patch.object(AllowlistEmailBackend, "_process_recipients")
    def test_send_messages_process_recipients_called(self, mocked_process_recipients, *args):
        backend = AllowlistEmailBackend()
        backend.send_messages([])

        mocked_process_recipients.assert_called_once_with([])

    @mock.patch.object(EmailBackend, "send_messages")
    def test_send_messages_super_called(self, mocked_send_messages):
        backend = AllowlistEmailBackend()
        backend.send_messages([])

        mocked_send_messages.assert_called_once_with([])

    def test_get_domain_allowlist_defaults_empty(self):
        self.assertEqual(AllowlistEmailBackend.get_domain_allowlist(), [])

    @override_settings(EMAIL_BACKEND_DOMAIN_WHITELIST=["legacy.domain"])
    def test_get_domain_allowlist_falls_back_to_whitelist(self):
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(AllowlistEmailBackend.get_domain_allowlist(), ["legacy.domain"])

    @override_settings(EMAIL_BACKEND_DOMAIN_ALLOWLIST=["allowed.domain"])
    def test_get_domain_whitelist_alias_warns(self):
        with self.assertWarns(DeprecationWarning):
            self.assertEqual(AllowlistEmailBackend.get_domain_whitelist(), ["allowed.domain"])

    @override_settings(EMAIL_BACKEND_DOMAIN_ALLOWLIST=["allowed.domain"])
    def test_get_email_regex_alias_warns(self):
        with self.assertWarns(DeprecationWarning):
            regex = AllowlistEmailBackend.get_email_regex()

        self.assertIn("allowed.domain", regex)

    def test_whitify_alias_warns(self):
        with self.assertWarns(DeprecationWarning):
            processed = AllowlistEmailBackend.whitify_mail_addresses(["platon@valid.domain"])
        self.assertEqual(processed, ["platon@valid.domain"])


class MailBackendWhitelistShimTest(TestCase):
    @override_settings(
        EMAIL_BACKEND_DOMAIN_WHITELIST=["legacy.domain"],
        EMAIL_BACKEND_REDIRECT_ADDRESS="%s@testuser.legacy.domain",
    )
    def test_shim_warns_and_redirects(self):
        with self.assertWarns(DeprecationWarning):
            backend = WhitelistEmailBackend()

        processed = backend.allowlist_mail_addresses(["user@legacy.domain", "other@example.com"])
        self.assertIn("user@legacy.domain", processed)
        self.assertIn("other_example.com@testuser.legacy.domain", processed)
