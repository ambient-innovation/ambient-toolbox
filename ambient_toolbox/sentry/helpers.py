def strip_sensitive_data_from_sentry_event(event, hint):
    """
    Helper method to strip sensitive user data from default sentry event when "send_default_pii" is set to True.
    All user-related data except the internal user id will be removed.
    Variable "hint" contains information about the error itself which we don't need here.
    Requires "sentry-sdk>=1.5.0" to work.
    """
    try:
        del event['user']['username']
    except KeyError:
        pass
    try:
        del event['user']['email']
    except KeyError:
        pass
    try:
        del event['user']['ip_address']
    except KeyError:
        pass
    return event
