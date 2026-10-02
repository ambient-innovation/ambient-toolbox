import re
import warnings
from collections.abc import Callable

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend


def build_email_regex(domains: list[str]) -> str:
    """Builds a regex pattern that matches email addresses on the given domains."""
    return r"^[\w\-\.]+@(%s)$" % "|".join(domains).replace(".", r"\.")


def filter_recipients(
    mail_address_list: list[str],
    get_email_regex: Callable[[], str],
    get_redirect_address: Callable[[], str],
) -> list[str]:
    """
    Keeps recipients matching the regex. Others are rewritten to the redirect address or dropped if it is empty.
    The getters are called lazily, so a missing redirect address only raises if a recipient needs redirecting.
    """
    allowed_recipients = []
    for to in mail_address_list:
        if re.search(get_email_regex(), to):
            allowed_recipients.append(to)
        elif get_redirect_address():
            # Send not allowed emails to the configured redirect address (with CATCHALL)
            allowed_recipients.append(get_redirect_address() % to.replace("@", "_"))
    return allowed_recipients


class AllowlistEmailBackend(SMTPEmailBackend):
    """
    Email backend that allows sending only to a configured set of domains.

    The getters call each other via the class name, so they can be patched on this class. To customise
    the filtering in a subclass, override `allowlist_mail_addresses()` or `_process_recipients()`.
    """

    @staticmethod
    def get_domain_allowlist() -> list[str]:
        """Returns the configured allowlist of email domains."""
        allowlist = getattr(settings, "EMAIL_BACKEND_DOMAIN_ALLOWLIST", None)
        if allowlist is not None:
            return allowlist

        legacy = getattr(settings, "EMAIL_BACKEND_DOMAIN_WHITELIST", None)
        if legacy is not None:
            # FutureWarning instead of DeprecationWarning: settings deprecations must be visible by default
            warnings.warn(
                "EMAIL_BACKEND_DOMAIN_WHITELIST is deprecated and will be removed in 13.0.0, "
                "use EMAIL_BACKEND_DOMAIN_ALLOWLIST",
                FutureWarning,
                stacklevel=2,
            )
            return legacy

        return []

    @staticmethod
    def get_email_allowlist_regex() -> str:
        """Builds a regex pattern that matches allowed domains."""
        return build_email_regex(AllowlistEmailBackend.get_domain_allowlist())

    @staticmethod
    def get_backend_redirect_address() -> str:
        """Returns the redirect catcher address. Raises AttributeError if it is not configured."""
        return settings.EMAIL_BACKEND_REDIRECT_ADDRESS

    @staticmethod
    def allowlist_mail_addresses(mail_address_list: list[str]) -> list[str]:
        """
        Keeps recipients on allowed domains. Others are rewritten to the configured redirect address
        or dropped if the redirect address is empty.
        """
        return filter_recipients(
            mail_address_list,
            AllowlistEmailBackend.get_email_allowlist_regex,
            AllowlistEmailBackend.get_backend_redirect_address,
        )

    def _process_recipients(self, email_messages):
        for email in email_messages:
            email.to = self.allowlist_mail_addresses(email.to)
        return email_messages

    def send_messages(self, email_messages):
        email_messages = self._process_recipients(email_messages)
        return super().send_messages(email_messages)
