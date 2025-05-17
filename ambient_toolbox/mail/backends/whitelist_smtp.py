import warnings


from ambient_toolbox.mail.backends.allowlist_smtp import AllowlistEmailBackend


class WhitelistEmailBackend(AllowlistEmailBackend):
    """
    The term "Whitelist" will be deprecated in 12.2 and move to "Allowlist".
    Until then, keep this for backwards compatibility but warn users about future deprecation.
    """

    def __init__(self, fail_silently=False, **kwargs):
        warnings.warn(
            "WhitelistEmailBackend is deprecated and will be removed in a future version. Use AllowlistEmailBackend instead.",
            category=DeprecationWarning,
            stacklevel=1,
        )
        super().__init__(fail_silently, **kwargs)
