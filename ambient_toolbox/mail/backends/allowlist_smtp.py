import re
import warnings

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend


class AllowlistEmailBackend(SMTPEmailBackend):
    """
    Via the following settings it is possible to configure if mails are sent to all domains.
    If not, you can configure a redirect to an inbox via CATCHALL.

    EMAIL_BACKEND = 'ambient_toolbox.mail.backends.allowlist_smtp.AllowlistEmailBackend'
    EMAIL_BACKEND_DOMAIN_ALLOWLIST = ['ambient.digital']
    EMAIL_BACKEND_REDIRECT_ADDRESS = '%s@testuser.ambient.digital'

    If `EMAIL_BACKEND_REDIRECT_ADDRESS` is set, a mail to `john.doe@example.com` will be redirected to
    `john.doe_example.com@testuser.ambient.digital`
    """

    # --------------------- deprecated methods START

    @staticmethod
    def get_domain_whitelist() -> list:
        """
        The term "Whitelist" will be deprecated in 12.2 and move to "Allowlist".
        Until then, keep this for backwards compatibility but warn users about future deprecation.
        """
        warnings.warn(
            "get_domain_whitelist() is deprecated. Use get_domain_allowlist() instead.",
            category=DeprecationWarning,
            stacklevel=1,
        )
        return AllowlistEmailBackend.get_domain_allowlist()

    @staticmethod
    def whitify_mail_addresses(mail_address_list: list) -> list:
        """
        The term "Whitelist" will be deprecated in 12.2 and move to "Allowlist".
        Until then, keep this for backwards compatibility but warn users about future deprecation.
        """
        warnings.warn(
            "whitify_mail_addresses() is deprecated. Use allowify_mail_addresses() instead.",
            category=DeprecationWarning,
            stacklevel=1,
        )
        return AllowlistEmailBackend.allowify_mail_addresses(mail_address_list=mail_address_list)

    # --------------------- deprecated methods END

    @staticmethod
    def get_domain_allowlist() -> list:
        """
        Getter for configuration variable from the settings.
        Will return a list of domains: ['ambient.digital', 'ambient.digital']
        """
        return getattr(settings, "EMAIL_BACKEND_DOMAIN_ALLOWLIST", [])

    @staticmethod
    def get_email_regex():
        """
        Getter for configuration variable from the settings.
        Will return a RegEX to match email allowlisted domains.
        """
        return r"^[\w\-\.]+@(%s)$" % "|".join(x for x in AllowlistEmailBackend.get_domain_allowlist()).replace(
            ".", r"\."
        )

    @staticmethod
    def get_backend_redirect_address() -> str:
        """
        Getter for configuration variable from the settings.
        Will return a string with a placeholder for redirecting non-allowlisted domains.
        """
        return settings.EMAIL_BACKEND_REDIRECT_ADDRESS

    @staticmethod
    def allowify_mail_addresses(mail_address_list: list) -> list:
        """
        Check for every recipient in the list if its domain is included in the allowlist.
        If not, and we have a redirect address configured, we change the original mail address to something new,
        according to our configuration.
        """
        allowed_recipients = []
        for to in mail_address_list:
            if re.search(AllowlistEmailBackend.get_email_regex(), to):
                allowed_recipients.append(to)
            elif AllowlistEmailBackend.get_backend_redirect_address():
                # Send not allowed emails to the configured redirect address (with CATCHALL)
                allowed_recipients.append(AllowlistEmailBackend.get_backend_redirect_address() % to.replace("@", "_"))
        return allowed_recipients

    def _process_recipients(self, email_messages):
        """
        Helper method to wrap custom logic of this backend. Required to make it testable.
        """
        for email in email_messages:
            allowed_recipients = self.allowify_mail_addresses(email.to)
            email.to = allowed_recipients
        return email_messages

    def send_messages(self, email_messages):
        """
        Checks if email-recipients are in allowed domains and cancels if not.
        Uses regular smtp-sending afterward.
        """
        email_messages = self._process_recipients(email_messages)
        return super().send_messages(email_messages)
