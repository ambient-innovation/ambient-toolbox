from django.db.models import manager


class Selector(manager.Manager):
    """
    This is the base class for query selectors. Please refer to the docs for further enlightenment how this novel
    pattern works.
    It's derived from the manager to use Django's magic to inject the current class into the "model" attribute.
    """

    model = None
