from typing import List, Optional

from sentry_sdk.serializer import serialize


class SentryEventScrubber:
    """
    Add this to the before_send and the before_send_transaction hook in order to remove all sensitive data from
    a Sentry event. It will also remove sensitive data in stacktraces.

    Usage:
    before_send = SentryEventScrubber().scrub_sensitive_data_from_sentry_event
    before_send_transaction = SentryEventScrubber().scrub_sensitive_data_from_sentry_event
    """

    def __init__(self, denylist: Optional[List[str]] = None, standard_denylist: Optional[bool] = True) -> None:
        """
        Arguments:
        * denylist: A list of keys that should be scrubbed from the Sentry event.
        * standard_denylist: By default certain keys are already scrubbed from the event.
        """
        self.denylist = [] if denylist is None else denylist
        self.standard_denylist = (
            [
                "username",
                "email",
                "ip_address",
                "serializer",
                "admin",
            ]
            if standard_denylist
            else []
        )

    def scrub_sensitive_data_from_sentry_event(self, event, _hint):
        from sentry_sdk.scrubber import DEFAULT_DENYLIST, EventScrubber

        EventScrubber(denylist=list(set(DEFAULT_DENYLIST + self.standard_denylist + self.denylist))).scrub_event(event)
        return serialize(event)


def strip_sensitive_data_from_sentry_event(event, hint):
    """
    A more lightweight way of cleaning sensitive data from the sentry event.

    Helper method to strip sensitive user data from default sentry event when "send_default_pii" is set to True.
    All user-related data except the internal user id will be removed.
    Variable "hint" contains information about the error itself which we don't need here.
    Requires "sentry-sdk>=1.5.0" to work.
    """
    try:
        del event["user"]["username"]
    except KeyError:
        pass
    try:
        del event["user"]["email"]
    except KeyError:
        pass
    try:
        del event["user"]["ip_address"]
    except KeyError:
        pass
    return event
