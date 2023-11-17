from contextvars import ContextVar
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

_request_cv: ContextVar[Optional["HttpRequest"]] = ContextVar("request", default=None)


class CurrentRequestMiddleware:
    """
    Middleware which stores the current request in a thread-safe manner.
    """

    def __init__(self, get_response: Callable[["HttpRequest"], "HttpResponse"]):
        self.get_response = get_response

    def __call__(self, request: "HttpRequest") -> "HttpResponse":
        token = _request_cv.set(request)
        response = self.get_response(request)
        _request_cv.reset(token)
        return response

    @staticmethod
    def get_current_user():
        request = _request_cv.get()
        try:
            return request.user
        except AttributeError:
            return None
