import threading
from http import HTTPStatus
from unittest.mock import Mock

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import TestCase

from ambient_toolbox.middleware.current_user import CurrentUserMiddleware


class CurrentUserMiddlewareTest(TestCase):
    def test_current_user_is_none_if_no_user_given(self):
        self.assertIsNone(CurrentUserMiddleware.get_current_user())

    def test_current_user_is_none_if_request_user_is_none(self):
        response = set_current_user(user=None)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_current_user_is_same_as_request_user(self):
        new_user = Mock(user_name="test_user")
        response = set_current_user(user=new_user)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_current_user_is_thread_safe(self):
        user1 = Mock(user_name="user1")
        user2 = Mock(user_name="user2")
        current_users = []
        ready_event = threading.Event()
        proceed_event = threading.Event()
        first_thread = threading.Thread(
            target=set_current_user,
            args=(user1, current_users, ready_event, proceed_event),
        )
        second_thread = threading.Thread(
            target=set_current_user,
            args=(user2, current_users),
        )
        first_thread.start()
        ready_event.wait()
        second_thread.start()
        second_thread.join()
        proceed_event.set()
        first_thread.join()
        self.assertEqual(current_users[0], user2)
        self.assertEqual(current_users[0].user_name, "user2")
        self.assertEqual(current_users[1], user1)
        self.assertEqual(current_users[1].user_name, "user1")

    def test_user_is_cleared_after_request(self):
        user = Mock(user_name="test_user")
        request = Mock(user=user)
        middleware = CurrentUserMiddleware(get_response=lambda request: HttpResponse(status=HTTPStatus.OK))
        response = middleware(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIsNone(CurrentUserMiddleware.get_current_user())

    def test_replaced_user_is_reflected_in_middleware(self):
        # This is roughly what happens when using eg. DRF token auth: during
        # middleware processing, request.user is an AnonymousUser, and at some
        # later point DRF replaces it with a user determined from given auth
        # info (eg. a token in the request header).
        # This should ideally be taken into account in our middleware since it
        # is also used to provide the user for `CommonInfo.lastmodified_by`.
        def get_response(request):
            replaced_user = Mock(user_name="replaced_user")
            request.user = replaced_user
            user_from_mw = CurrentUserMiddleware.get_current_user()
            if user_from_mw is not replaced_user:
                return HttpResponse(status=HTTPStatus.CONFLICT)  # pragma: no cover
            return HttpResponse(status=HTTPStatus.OK)

        middleware = CurrentUserMiddleware(get_response)
        anonymous_user = AnonymousUser()
        request = Mock(user=anonymous_user)
        response = middleware(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)


def set_current_user(user=None, current_users=None, ready_event=None, proceed_event=None):
    def get_response(request):
        if ready_event is not None:
            ready_event.set()
        if proceed_event is not None:
            proceed_event.wait()
        user_from_mw = CurrentUserMiddleware.get_current_user()
        if current_users is not None:
            current_users.append(user_from_mw)
        if user_from_mw is not request.user:
            return HttpResponse(status=HTTPStatus.CONFLICT)  # pragma: no cover
        if user_from_mw is None:
            return HttpResponse(status=HTTPStatus.NO_CONTENT)
        return HttpResponse(status=HTTPStatus.OK)

    middleware = CurrentUserMiddleware(get_response)
    request = Mock()
    request.user = user
    return middleware(request)
