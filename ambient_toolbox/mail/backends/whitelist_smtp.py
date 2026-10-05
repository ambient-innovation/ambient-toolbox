import warnings

from ambient_toolbox.mail.backends.allowlist_smtp import AllowlistEmailBackend, build_email_regex, filter_recipients

DEPRECATION_MESSAGE = (
    "ambient_toolbox.mail.backends.whitelist_smtp.WhitelistEmailBackend is deprecated and will be removed in 13.0.0, "
    "use ambient_toolbox.mail.backends.allowlist_smtp.AllowlistEmailBackend instead."
)


class WhitelistEmailBackend(AllowlistEmailBackend):
    """
    Deprecated shim keeping the old import path and method names intact. Behaves exactly like before the rename:

    - Sending calls `self.whitify_mail_addresses()`, so subclasses overriding it keep working.
    - The old methods call each other via the class name `WhitelistEmailBackend`, so patching
      `get_domain_whitelist()`, `get_email_regex()` or `get_backend_redirect_address()` on this class
      keeps working. Subclass overrides of these three are not used, just like before.
    """

    def __init_subclass__(cls, **kwargs):
        warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)
        super().__init_subclass__(**kwargs)

    def __init__(self, *args, **kwargs):
        # FutureWarning: most projects only reference this class in the EMAIL_BACKEND setting, so Django instantiates
        # it and a DeprecationWarning attributed to Django's code would be hidden by default
        warnings.warn(DEPRECATION_MESSAGE, FutureWarning, stacklevel=2)
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_domain_whitelist() -> list[str]:
        return AllowlistEmailBackend.get_domain_allowlist()

    @staticmethod
    def get_email_regex() -> str:
        return build_email_regex(WhitelistEmailBackend.get_domain_whitelist())

    @staticmethod
    def whitify_mail_addresses(mail_address_list: list[str]) -> list[str]:
        return filter_recipients(
            mail_address_list,
            WhitelistEmailBackend.get_email_regex,
            WhitelistEmailBackend.get_backend_redirect_address,
        )

    def _process_recipients(self, email_messages):
        for email in email_messages:
            email.to = self.whitify_mail_addresses(email.to)
        return email_messages
