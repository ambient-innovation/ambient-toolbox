from typing import Optional, Union

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.test import RequestFactory
from django.utils.translation import gettext_lazy as _


class ClassBasedViewTestMixin:
    """
    Helper mixin for easy testing of Django views
    """

    factory_class = RequestFactory
    view_class = None

    @staticmethod
    def _authentication(request, user):
        request.user = user if user else AnonymousUser()

    def _get_response(self, method, user, data, url_params=None, *args, **kwargs):
        """Returns response."""

        # Catch case that URL does not get any params passed to
        if not url_params:
            url_params = {}

        # Create request
        factory = self.factory_class()
        req_kwargs = {}
        if data:
            req_kwargs.update({"data": data})
        request = getattr(factory, method)("/", **req_kwargs)

        # Annotate a request object with a session
        middleware = SessionMiddleware(get_response=HttpResponse(status=200))
        middleware.process_request(request)
        request.session.save()

        # Authenticate user
        self._authentication(request, user)

        # Setup messages
        messages = FallbackStorage(request)
        request._messages = messages

        # Call view
        return self.view_class.as_view()(request, *args, **url_params)

    def get(self, user=None, data=None, url_params=None, *args, **kwargs):
        """Returns response for a GET request."""
        return self._get_response("get", user, data, url_params, *args, **kwargs)

    def post(self, user=None, data=None, url_params=None, *args, **kwargs):
        """Returns response for a POST request."""
        return self._get_response("post", user, data, url_params, *args, **kwargs)

    def delete(self, user=None, data=None, url_params=None, *args, **kwargs):
        """Returns response for a DELETE request."""
        return self._get_response("delete", user, data, url_params, *args, **kwargs)


class RequestProviderMixin:
    """
    Mixin that provides a method which returns a django request.
    Supposed to be used in unittests that require a request object.
    Also adds the message middleware so django messages can be tested.
    """

    @staticmethod
    def get_request(
        user: Union[AbstractBaseUser, AnonymousUser, None] = None, method: str = "GET", url: Optional[str] = None
    ):
        """
        Creates and returns a django request.
        """
        # Determine URL
        url = url if url else "/"

        # Create test request
        factory = RequestFactory()
        request = factory.get(url)

        # Set user object if it is of a valid type
        # TODO: remove noqa when we drop older python support
        if user is None or isinstance(user, AbstractBaseUser) or isinstance(user, AnonymousUser):  # noqa: PLR1701
            request.user = user
        else:
            raise ValueError(_("Please pass a user object to RequestProviderMixin."))

        # Annotate a request object with a session
        session_middleware = SessionMiddleware(get_response=HttpResponse(status=200))
        session_middleware.process_request(request)
        request.session.save()

        # Annotate a request object with messages
        message_middleware = MessageMiddleware(get_response=HttpResponse(status=200))
        message_middleware.process_request(request)
        request.session.save()

        # Set request method
        request.method = method

        return request


class DjangoMessagingFrameworkTestMixin:
    """
    Mixin to enable test cases to easily check for messages in the request.
    This test is made for the Django Messaging Framework.
    """

    def assert_full_message_in_request(self, request: WSGIRequest, message: str) -> None:
        messages = list(get_messages(request))

        self.assertGreater(len(messages), 0, "The request doesn't contain any messages.")
        message_found = False
        for request_message in messages:
            if str(request_message) == message:
                message_found = True

        self.assertTrue(message_found, f"Message {message!r} not found in request.")

    def assert_partial_message_in_request(self, request: WSGIRequest, message: str) -> None:
        messages = list(get_messages(request))

        self.assertGreater(len(messages), 0, "The request doesn't contain any messages.")

        message_found = False
        for request_message in messages:
            if message in str(request_message):
                message_found = True

        self.assertTrue(message_found, f"Message part {message!r} not found in request.")

    def assert_message_not_in_request(self, request: WSGIRequest, message: str) -> None:
        messages = list(get_messages(request))

        message_found = False
        for request_message in messages:
            if str(request_message) == message:
                message_found = True

        self.assertFalse(message_found, f"Message {message!r} not found in request.")
