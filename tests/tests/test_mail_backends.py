import warnings
from unittest import mock

from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.test import TestCase, override_settings

from ambient_toolbox.mail.backends.allowlist_smtp import AllowlistEmailBackend


@override_settings(
    EMAIL_BACKEND="ambient_toolbox.mail.backends.allowlist_smtp.AllowlistEmailBackend",
    EMAIL_BACKEND_DOMAIN_ALLOWLIST=["valid.domain"],
    EMAIL_BACKEND_REDIRECT_ADDRESS="%s@testuser.valid.domain",
)
class MailBackendAllowlistBackendTest(TestCase):
    # --------------------- deprecated methods START

    def test_get_domain_whitelist_warns_about_deprecation_and_calls_get_domain_allowlist(self):
        with (
            mock.patch.object(warnings, "warn") as mocked_warn,
            mock.patch.object(AllowlistEmailBackend, "get_domain_allowlist") as mocked_get_domain_allowlist,
        ):
            AllowlistEmailBackend.get_domain_whitelist()

        mocked_warn.assert_called_once_with(
            "get_domain_whitelist() is deprecated and will be removed in a future version."
            "Use get_domain_allowlist() instead.",
            category=DeprecationWarning,
            stacklevel=1,
        )

        mocked_get_domain_allowlist.assert_called_once()

    def test_whitify_mail_addresses_warns_about_deprecation_and_calls_allowify_mail_addresses(self):
        with (
            mock.patch.object(warnings, "warn") as mocked_warn,
            mock.patch.object(AllowlistEmailBackend, "allowify_mail_addresses") as mocked_allowify_mail_addresses,
        ):
            AllowlistEmailBackend.whitify_mail_addresses(mail_address_list=[])

        mocked_warn.assert_called_once_with(
            "whitify_mail_addresses() is deprecated and will be removed in a future version."
            "Use allowify_mail_addresses() instead.",
            category=DeprecationWarning,
            stacklevel=1,
        )

        mocked_allowify_mail_addresses.assert_called_once_with(mail_address_list=[])

    # --------------------- deprecated methods END

    def test_allowify_mail_addresses_replace(self):
        email_1 = "albertus.magnus@example.com"
        email_2 = "thomas_von_aquin@example.com"
        processed_list = AllowlistEmailBackend.allowify_mail_addresses(mail_address_list=[email_1, email_2])

        self.assertEqual(len(processed_list), 2)
        self.assertEqual(processed_list[0], "albertus.magnus_example.com@testuser.valid.domain")
        self.assertEqual(processed_list[1], "thomas_von_aquin_example.com@testuser.valid.domain")

    def test_allowify_mail_addresses_allowlisted_domain(self):
        email = "platon@valid.domain"
        processed_list = AllowlistEmailBackend.allowify_mail_addresses(mail_address_list=[email])

        self.assertEqual(len(processed_list), 1)
        self.assertEqual(processed_list[0], email)

    @override_settings(EMAIL_BACKEND_REDIRECT_ADDRESS="")
    def test_allowify_mail_addresses_no_redirect_configured(self):
        email = "sokrates@example.com"
        processed_list = AllowlistEmailBackend.allowify_mail_addresses(mail_address_list=[email])

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
