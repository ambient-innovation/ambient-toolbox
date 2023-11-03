import warnings
from typing import TYPE_CHECKING, Callable

from .current_request import CurrentRequestMiddleware

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


class CurrentUserMiddleware(CurrentRequestMiddleware):
    """
    Middleware which stores the current user in a thread-safe manner.

    This middleware is deprecated, use CurrentRequestMiddleware instead.
    """

    # Tech Note: This class is now a mere alias for CurrentRequestMiddleware to
    # provide backward compatibility. This whole module can be removed as part
    # of one of the next major releases, then fully dropping support for
    # CurrentUserMiddleware.

    def __init__(self, get_response: Callable[["HttpRequest"], "HttpResponse"]):
        warnings.warn(
            "CurrentUserMiddleware is deprecated. Use CurrentRequestMiddleware instead.",
            category=DeprecationWarning,
            stacklevel=1,
        )
        super().__init__(get_response)
