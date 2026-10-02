import re
import types
import warnings

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend


class Hook:
    """
    Binds to the instance when accessed on one, otherwise to the class (so `self` may be the class).

    Lets the recipient hooks be called on the class (legacy static API) while overrides written as
    instance methods are still used on the regular send path, which always calls them on the instance.
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, objtype=None):
        return types.MethodType(self.func, objtype if obj is None else obj)


class AllowlistEmailBackend(SMTPEmailBackend):
    """Email backend that allows sending only to a configured set of domains."""

    DOMAIN_ALLOWLIST_SETTING = "EMAIL_BACKEND_DOMAIN_ALLOWLIST"
    DOMAIN_WHITELIST_SETTING = "EMAIL_BACKEND_DOMAIN_WHITELIST"

    @classmethod
    def _get_domain_allowlist_setting(cls) -> list[str]:
        allowlist = getattr(settings, cls.DOMAIN_ALLOWLIST_SETTING, None)
        if allowlist is not None:
            return allowlist

        legacy = getattr(settings, cls.DOMAIN_WHITELIST_SETTING, None)
        if legacy is not None:
            # FutureWarning instead of DeprecationWarning: settings deprecations must be visible by default
            warnings.warn(
                f"{cls.DOMAIN_WHITELIST_SETTING} is deprecated and will be removed in 13.0.0, "
                f"use {cls.DOMAIN_ALLOWLIST_SETTING}",
                FutureWarning,
                stacklevel=3,
            )
            return legacy

        return []

    @Hook
    def get_domain_allowlist(self) -> list[str]:
        """Returns the configured allowlist of email domains."""
        return self._get_domain_allowlist_setting()

    @Hook
    def get_email_allowlist_regex(self) -> str:
        """Builds a regex pattern that matches allowed domains."""
        pattern = r"|".join(self.get_domain_allowlist()).replace(".", r"\.")
        return r"^[\w\-\.]+@(%s)$" % pattern

    @staticmethod
    def get_backend_redirect_address() -> str:
        """Returns the redirect catcher address. Raises AttributeError if it is not configured."""
        return settings.EMAIL_BACKEND_REDIRECT_ADDRESS

    @Hook
    def allowlist_mail_addresses(self, mail_address_list: list[str]) -> list[str]:
        """
        Keeps recipients on allowed domains. Others are rewritten to the configured redirect address
        or dropped if no redirect address is set.
        """
        allowed_recipients: list[str] = []
        for to in mail_address_list:
            if re.search(self.get_email_allowlist_regex(), to):
                allowed_recipients.append(to)
            elif self.get_backend_redirect_address():
                allowed_recipients.append(self.get_backend_redirect_address() % to.replace("@", "_"))
        return allowed_recipients

    def _process_recipients(self, email_messages):
        for email in email_messages:
            email.to = self.allowlist_mail_addresses(email.to)
        return email_messages

    def send_messages(self, email_messages):
        email_messages = self._process_recipients(email_messages)
        return super().send_messages(email_messages)
