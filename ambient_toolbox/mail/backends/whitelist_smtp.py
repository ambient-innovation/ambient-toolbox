import warnings

from ambient_toolbox.mail.backends.allowlist_smtp import AllowlistEmailBackend

DEPRECATION_MESSAGE = (
    "ambient_toolbox.mail.backends.whitelist_smtp.WhitelistEmailBackend is deprecated and will be removed in 13.0.0, "
    "use ambient_toolbox.mail.backends.allowlist_smtp.AllowlistEmailBackend instead."
)


class WhitelistEmailBackend(AllowlistEmailBackend):
    """
    Deprecated shim keeping the old import path and hook names intact.

    The new method names delegate to the legacy ones, so subclasses overriding (or tests patching)
    `get_domain_whitelist()`, `get_email_regex()` or `whitify_mail_addresses()` keep working.
    The legacy methods call the `AllowlistEmailBackend` implementation, so `super()` calls in overrides are safe.
    """

    def __init_subclass__(cls, **kwargs):
        warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)
        super().__init_subclass__(**kwargs)

    def __init__(self, *args, **kwargs):
        warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)

    # Legacy hooks -> new implementation
    @classmethod
    def get_domain_whitelist(cls) -> list[str]:
        return super().get_domain_allowlist()

    @classmethod
    def get_email_regex(cls) -> str:
        return super().get_email_allowlist_regex()

    @classmethod
    def whitify_mail_addresses(cls, mail_address_list: list[str]) -> list[str]:
        return super().allowlist_mail_addresses(mail_address_list)

    # New names -> legacy hooks, so overrides of the legacy hooks take effect
    @classmethod
    def get_domain_allowlist(cls) -> list[str]:
        return cls.get_domain_whitelist()

    @classmethod
    def get_email_allowlist_regex(cls) -> str:
        return cls.get_email_regex()

    @classmethod
    def allowlist_mail_addresses(cls, mail_address_list: list[str]) -> list[str]:
        return cls.whitify_mail_addresses(mail_address_list)
