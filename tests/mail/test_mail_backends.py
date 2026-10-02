from unittest import mock

from django.conf import settings
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
        with self.settings(
            EMAIL_BACKEND_DOMAIN_ALLOWLIST=None,
            EMAIL_BACKEND_DOMAIN_WHITELIST=None,
        ):
            self.assertEqual(AllowlistEmailBackend.get_domain_allowlist(), [])

    def test_get_domain_allowlist_falls_back_to_whitelist(self):
        with self.settings(
            EMAIL_BACKEND_DOMAIN_ALLOWLIST=None,
            EMAIL_BACKEND_DOMAIN_WHITELIST=["legacy.domain"],
        ):
            with self.assertWarns(FutureWarning) as cm:
                self.assertEqual(AllowlistEmailBackend.get_domain_allowlist(), ["legacy.domain"])

        self.assertIn("will be removed in 13.0.0", str(cm.warning))
        # stacklevel must point past the internal helper to the caller of the getter
        self.assertEqual(cm.filename, __file__)

    @override_settings()
    def test_missing_redirect_address_raises(self):
        del settings.EMAIL_BACKEND_REDIRECT_ADDRESS

        with self.assertRaises(AttributeError):
            AllowlistEmailBackend.allowlist_mail_addresses(["sokrates@example.com"])


@override_settings(
    EMAIL_BACKEND_DOMAIN_ALLOWLIST=["valid.domain"],
    EMAIL_BACKEND_REDIRECT_ADDRESS="%s@testuser.valid.domain",
)
class MailBackendWhitelistShimTest(TestCase):
    def setUp(self):
        with self.assertWarns(DeprecationWarning):
            self.backend = WhitelistEmailBackend()

    @override_settings(
        EMAIL_BACKEND_DOMAIN_ALLOWLIST=None,
        EMAIL_BACKEND_DOMAIN_WHITELIST=["legacy.domain"],
        EMAIL_BACKEND_REDIRECT_ADDRESS="%s@testuser.legacy.domain",
    )
    def test_shim_redirects_with_legacy_setting(self):
        with self.assertWarns(FutureWarning):
            processed = self.backend.allowlist_mail_addresses(["user@legacy.domain", "other@example.com"])

        self.assertEqual(processed, ["user@legacy.domain", "other_example.com@testuser.legacy.domain"])

    def test_legacy_methods_delegate_to_new_implementation(self):
        self.assertEqual(WhitelistEmailBackend.get_domain_whitelist(), ["valid.domain"])
        self.assertEqual(WhitelistEmailBackend.get_email_regex(), AllowlistEmailBackend.get_email_allowlist_regex())
        self.assertEqual(WhitelistEmailBackend.whitify_mail_addresses(["platon@valid.domain"]), ["platon@valid.domain"])

    def test_subclassing_warns(self):
        with self.assertWarns(DeprecationWarning):

            class CustomBackend(WhitelistEmailBackend):
                pass

    def test_overridden_whitify_mail_addresses_is_used(self):
        with self.assertWarns(DeprecationWarning):

            class CustomBackend(WhitelistEmailBackend):
                @staticmethod
                def whitify_mail_addresses(mail_address_list):
                    return ["custom@valid.domain"]

        with self.assertWarns(DeprecationWarning):
            backend = CustomBackend()
        mail = EmailMultiAlternatives("Subject", "Body", "from@example.com", ["to@example.com"])

        self.assertEqual(backend._process_recipients([mail])[0].to, ["custom@valid.domain"])

    def test_overridden_get_domain_whitelist_with_super_is_used(self):
        with self.assertWarns(DeprecationWarning):

            class CustomBackend(WhitelistEmailBackend):
                @classmethod
                def get_domain_whitelist(cls):
                    return [*super().get_domain_whitelist(), "extra.domain"]

        self.assertEqual(CustomBackend.allowlist_mail_addresses(["a@extra.domain"]), ["a@extra.domain"])

    def test_patched_legacy_hooks_are_used(self):
        with mock.patch.object(WhitelistEmailBackend, "get_domain_whitelist", return_value=["patched.domain"]):
            self.assertEqual(self.backend.allowlist_mail_addresses(["a@patched.domain"]), ["a@patched.domain"])

        with mock.patch.object(WhitelistEmailBackend, "get_email_regex", return_value=r"^never$"):
            self.assertEqual(
                self.backend.allowlist_mail_addresses(["a@valid.domain"]), ["a_valid.domain@testuser.valid.domain"]
            )
