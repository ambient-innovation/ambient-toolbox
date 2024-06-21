# Sentry

Sentry is an open-source bugtracker. Read more at https://sentry.io/.

## Send GDPR-compliant user data

When gathering data on a crash, the current user can be of major importance. Sentry offers a simple way of sending all
user-related data to your Sentry instance. Unfortunately, this collides with GDPR because IP and email address are
sensitive data. Luckily, the internal user id is not.

So if you are using the default django authentication process, you can easily set up Sentry, so you get the user id in
your error reports but nothing else (what might conflict with GDPR).

### Sentry client

Install the latest `sentry-sdk` client from pypi:

    pip install -U sentry-sdk

Or for django integration:

    pip install --upgrade 'sentry-sdk[django]'

For more information please read the official [documentation](https://docs.sentry.io/platforms/python/guides/django/)
on Sentry's Django integration.

### Settings

There are a hand full important settings to be aware of when using Sentry:
- [send_default_pii](https://docs.sentry.io/platforms/python/guides/django/configuration/options/#send-default-pii)
- [event_scrubber](https://docs.sentry.io/platforms/python/guides/django/configuration/options/#event-scrubber)
- [before_send](https://docs.sentry.io/platforms/python/guides/django/configuration/options/#before-send)
- [before_send_transaction](https://docs.sentry.io/platforms/python/guides/django/configuration/options/#before-send-transaction)
- [request_bodies](https://docs.sentry.io/platforms/python/guides/django/configuration/options/#before-send-transaction)

To send GDPR conform data to Sentry adjust the settings in the main `settings.py` as follows:

```python
from ambient_toolbox.sentry.helpers import SentryEventScrubber
import sentry_sdk

sentry_sdk.init(
    send_default_pii=True,
    before_send=SentryEventScrubber().scrub_sensitive_data_from_sentry_event,
    before_send_transaction=SentryEventScrubber().scrub_sensitive_data_from_sentry_event,
    ...,
)
```

The `send_default_pii` attaches some additional information to the event. If turned on the default `event_scrubber` will
not run automatically therefore the `before_send` and `before_send_transaction` hook have to be set to remove all
sensitive data. One way to remove the data is to use the `SentryEventScrubber`. It will remove all sensitive data from
the event, no matter if it is part of the user data or in the stacktrace. It is also possible to specify more keys to be
removed from the event by passing in a `denylist` with a list of names.

There is also a more lightweight way of removing sensitive data that will only remove data on the user object and
therefore might miss sensitive data within e.g. the stacktrace, on the other hand it offers more context on the event.
To use this lightweight event scrubber use the following settings instead:

```python
from ambient_toolbox.sentry.helpers import strip_sensitive_data_from_sentry_event
import sentry_sdk

sentry_sdk.init(
    send_default_pii=True,
    before_send=strip_sensitive_data_from_sentry_event,
    before_send_transaction=strip_sensitive_data_from_sentry_event,
    ...,
)
```

And that's it! Have fun finding your bugs more easily!
