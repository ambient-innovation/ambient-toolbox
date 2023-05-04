# Sentry

Sentry is an open-source bugtracker. Read more at https://sentry.io/.

## Send GDPR-compliant user data

When gathering data on a crash, the current user can be of major importance. Sentry offers a simple way of sending all
user-related data to your Sentry instance. Unfortunately, this collides with GDPR because IP and email address are
sensitive data. Luckily, the internal user id is not.

So if you are using the default django authentication process, you can easily set up Sentry, so you get the user id in
your error reports but nothing else (what might conflict with GDPR).

### Sentry client

Install the latest `sentry-sdk` client from pypi.

    pip install -U sentry-sdk

### Settings

Adjust in your main `settings.py` your sentry setup as follows:

    from ambient_toolbox.sentry.helpers import strip_sensitive_data_from_sentry_event

    sentry_sdk.init(
        ...
        send_default_pii=True,
        before_send=strip_sensitive_data_from_sentry_event,
    )

And that's it! Have fun finding your bugs more easily!
