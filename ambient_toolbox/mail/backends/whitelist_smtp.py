import warnings

from ambient_toolbox.mail.backends.allowlist_smtp import AllowlistEmailBackend, Hook

DEPRECATION_MESSAGE = (
    "ambient_toolbox.mail.backends.whitelist_smtp.WhitelistEmailBackend is deprecated and will be removed in 13.0.0, "
    "use ambient_toolbox.mail.backends.allowlist_smtp.AllowlistEmailBackend instead."
)


class WhitelistEmailBackend(AllowlistEmailBackend):
    """
    Deprecated shim keeping the old import path and hook names intact.

    The new method names delegate to the legacy ones, so subclasses overriding (or tests patching)
    `get_domain_whitelist()`, `get_email_regex()`, `whitify_mail_addresses()` or `get_backend_redirect_address()`
    keep working, whether the override is a static, class or instance method. The legacy methods call the
    `AllowlistEmailBackend` implementation, so `super()` calls in overrides are safe.
    """

    def __init_subclass__(cls, **kwargs):
        warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)
        super().__init_subclass__(**kwargs)

    def __init__(self, *args, **kwargs):
        warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)

    # Legacy hooks -> new implementation
    @Hook
    def get_domain_whitelist(self) -> list[str]:
        return super().get_domain_allowlist()

    @Hook
    def get_email_regex(self) -> str:
        return super().get_email_allowlist_regex()

    @Hook
    def whitify_mail_addresses(self, mail_address_list: list[str]) -> list[str]:
        return super().allowlist_mail_addresses(mail_address_list)

    # New names -> legacy hooks, so overrides of the legacy hooks take effect
    @Hook
    def get_domain_allowlist(self) -> list[str]:
        return self.get_domain_whitelist()

    @Hook
    def get_email_allowlist_regex(self) -> str:
        return self.get_email_regex()

    @Hook
    def allowlist_mail_addresses(self, mail_address_list: list[str]) -> list[str]:
        return self.whitify_mail_addresses(mail_address_list)
