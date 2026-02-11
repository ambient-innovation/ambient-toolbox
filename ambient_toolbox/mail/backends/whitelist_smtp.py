import warnings

from ambient_toolbox.mail.backends.allowlist_smtp import AllowlistEmailBackend


class WhitelistEmailBackend(AllowlistEmailBackend):
    """Deprecated shim keeping the old import path intact."""

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "ambient_toolbox.mail.backends.whitelist_smtp.WhitelistEmailBackend is deprecated, "
            "use AllowlistEmailBackend instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
