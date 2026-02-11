import re
import warnings

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend


class AllowlistEmailBackend(SMTPEmailBackend):
    """Email backend that allows sending only to a configured set of domains."""

    DOMAIN_ALLOWLIST_SETTING = "EMAIL_BACKEND_DOMAIN_ALLOWLIST"
    DOMAIN_WHITELIST_SETTING = "EMAIL_BACKEND_DOMAIN_WHITELIST"
    REDIRECT_ADDRESS_SETTING = "EMAIL_BACKEND_REDIRECT_ADDRESS"

    @classmethod
    def _get_domain_allowlist_setting(cls) -> list[str]:
        allowlist = getattr(settings, cls.DOMAIN_ALLOWLIST_SETTING, None)
        if allowlist is not None:
            return allowlist

        legacy = getattr(settings, cls.DOMAIN_WHITELIST_SETTING, None)
        if legacy is not None:
            warnings.warn(
                f"{cls.DOMAIN_WHITELIST_SETTING} is deprecated, use {cls.DOMAIN_ALLOWLIST_SETTING}",
                DeprecationWarning,
                stacklevel=2,
            )
            return legacy

        return []

    @staticmethod
    def get_domain_allowlist() -> list[str]:
        """Returns the configured allowlist of email domains."""
        return AllowlistEmailBackend._get_domain_allowlist_setting()

    @staticmethod
    def get_domain_whitelist() -> list[str]:
        """Deprecated alias kept for backwards compatibility."""
        warnings.warn(
            "AllowlistEmailBackend.get_domain_whitelist() is deprecated, use get_domain_allowlist()",
            DeprecationWarning,
            stacklevel=2,
        )
        return AllowlistEmailBackend.get_domain_allowlist()

    @staticmethod
    def get_email_allowlist_regex() -> str:
        """Builds a regex pattern that matches allowed domains."""
        domains = AllowlistEmailBackend.get_domain_allowlist()
        pattern = r"|".join(x for x in domains).replace(".", r"\.")
        return r"^[\w\-\.]+@(%s)$" % pattern

    @staticmethod
    def get_email_regex() -> str:
        """Deprecated alias kept for backwards compatibility."""
        warnings.warn(
            "AllowlistEmailBackend.get_email_regex() is deprecated, use get_email_allowlist_regex()",
            DeprecationWarning,
            stacklevel=2,
        )
        return AllowlistEmailBackend.get_email_allowlist_regex()

    @staticmethod
    def get_backend_redirect_address() -> str | None:
        """Returns the optional redirect catcher address."""
        return getattr(settings, AllowlistEmailBackend.REDIRECT_ADDRESS_SETTING, None)

    @staticmethod
    def allowlist_mail_addresses(mail_address_list: list[str]) -> list[str]:
        allowed_recipients: list[str] = []
        for to in mail_address_list:
            if re.search(AllowlistEmailBackend.get_email_allowlist_regex(), to):
                allowed_recipients.append(to)
            elif AllowlistEmailBackend.get_backend_redirect_address():
                allowed_recipients.append(AllowlistEmailBackend.get_backend_redirect_address() % to.replace("@", "_"))
        return allowed_recipients

    @staticmethod
    def whitify_mail_addresses(mail_address_list: list[str]) -> list[str]:
        warnings.warn(
            "AllowlistEmailBackend.whitify_mail_addresses() is deprecated, use allowlist_mail_addresses()",
            DeprecationWarning,
            stacklevel=2,
        )
        return AllowlistEmailBackend.allowlist_mail_addresses(mail_address_list)

    def _process_recipients(self, email_messages):
        for email in email_messages:
            allowed_recipients = self.allowlist_mail_addresses(email.to)
            email.to = allowed_recipients
        return email_messages

    def send_messages(self, email_messages):
        email_messages = self._process_recipients(email_messages)
        return super().send_messages(email_messages)


EMAIL_BACKEND = "ambient_toolbox.mail.backends.allowlist_smtp.AllowlistEmailBackend"
