# Mailing

## Backends

### AllowlistEmailBackend

In some cases it is useful to debug and test email functionality on local or test environments. Additionally, your
project could contain logic that triggers emails in the background, so it is very important that you don't send emails
to other domains, e.g. `xyz@test.de` or to other test users with another domain, by accident.

This email backend can be used as Django `EMAIL_BACKEND` to restrict outgoing emails to a set of allowed domains. You can
define an email address (must be a catchall inbox) where the restricted emails should be redirected to.

Example:

```python
EMAIL_BACKEND = "ambient_toolbox.mail.backends.allowlist_smtp.AllowlistEmailBackend"
EMAIL_BACKEND_DOMAIN_ALLOWLIST = ["beyonder.de"]
EMAIL_BACKEND_REDIRECT_ADDRESS = "%s@testuser.beyonder.de"
```

If the legacy `EMAIL_BACKEND_DOMAIN_WHITELIST` setting is still configured, the backend reads it while emitting a
`FutureWarning`. The old `ambient_toolbox.mail.backends.whitelist_smtp.WhitelistEmailBackend` path is kept as a shim
that emits a `DeprecationWarning` and behaves exactly as before the rename:

- Sending calls `self.whitify_mail_addresses()`, so overriding it in a subclass keeps working, no matter whether the
  override is a static, class or instance method.
- `get_domain_whitelist()`, `get_email_regex()`, `whitify_mail_addresses()` and `get_backend_redirect_address()` call
  each other via the class name `WhitelistEmailBackend`. Patching them on that class (also with `autospec=True`) keeps
  working, but subclass overrides of `get_domain_whitelist()`, `get_email_regex()` and
  `get_backend_redirect_address()` are not used.

`AllowlistEmailBackend` works the same way with its new method names: to customise the filtering in a subclass,
override `allowlist_mail_addresses()` or `_process_recipients()`. Both legacy names will be removed in 13.0.0.

If EMAIL_BACKEND_REDIRECT_ADDRESS is configured, an email to 'albertus.magnus@example.com' will be redirected to:
albertus.magnus_example.com@testuser.beyonder.de
