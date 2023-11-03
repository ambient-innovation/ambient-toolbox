import re

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend


class WhitelistEmailBackend(SMTPEmailBackend):
    """
    Via the following settings it is possible to configure if mails are sent to all domains.
    If not, you can configure a redirect to an inbox via CATCHALL.

    EMAIL_BACKEND = 'ambient_toolbox.mail.backends.whitelist_smtp.WhitelistEmailBackend'
    EMAIL_BACKEND_DOMAIN_WHITELIST = ['ambient.digital']
    EMAIL_BACKEND_REDIRECT_ADDRESS = '%s@testuser.ambient.digital'

    If `EMAIL_BACKEND_REDIRECT_ADDRESS` is set, a mail to `john.doe@example.com` will be redirected to
    `john.doe_example.com@testuser.ambient.digital`
    """

    @staticmethod
    def get_domain_whitelist() -> list:
        """
        Getter for configuration variable from the settings.
        Will return a list of domains: ['ambient.digital', 'ambient.digital']
        """
        return getattr(settings, "EMAIL_BACKEND_DOMAIN_WHITELIST", [])

    @staticmethod
    def get_email_regex():
        """
        Getter for configuration variable from the settings.
        Will return a RegEX to match email whitelisted domains.
        """
        return r"^[\w\-\.]+@(%s)$" % "|".join(x for x in WhitelistEmailBackend.get_domain_whitelist()).replace(
            ".", r"\."
        )

    @staticmethod
    def get_backend_redirect_address() -> str:
        """
        Getter for configuration variable from the settings.
        Will return a string with a placeholder for redirecting non-whitelisted domains.
        """
        return settings.EMAIL_BACKEND_REDIRECT_ADDRESS

    @staticmethod
    def whitify_mail_addresses(mail_address_list: list) -> list:
        """
        Check for every recipient in the list if its domain is included in the whitelist.
        If not, and we have a redirect address configured, we change the original mail address to something new,
        according to our configuration.
        """
        allowed_recipients = []
        for to in mail_address_list:
            if re.search(WhitelistEmailBackend.get_email_regex(), to):
                allowed_recipients.append(to)
            elif WhitelistEmailBackend.get_backend_redirect_address():
                # Send not allowed emails to the configured redirect address (with CATCHALL)
                allowed_recipients.append(WhitelistEmailBackend.get_backend_redirect_address() % to.replace("@", "_"))
        return allowed_recipients

    def _process_recipients(self, email_messages):
        """
        Helper method to wrap custom logic of this backend. Required to make it testable.
        """
        for email in email_messages:
            allowed_recipients = self.whitify_mail_addresses(email.to)
            email.to = allowed_recipients
        return email_messages

    def send_messages(self, email_messages):
        """
        Checks if email-recipients are in allowed domains and cancels if not.
        Uses regular smtp-sending afterward.
        """
        email_messages = self._process_recipients(email_messages)
        return super().send_messages(email_messages)
