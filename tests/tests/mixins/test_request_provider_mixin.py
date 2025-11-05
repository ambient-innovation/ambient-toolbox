from django.contrib import messages
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest
from django.test import TestCase

from ambient_toolbox.tests.mixins import RequestProviderMixin
from testapp.models import MySingleSignalModel


class RequestProviderMixinTest(RequestProviderMixin, TestCase):
    def test_request_is_request(self):
        request = self.get_request(None)
        self.assertIsInstance(request, HttpRequest)

    def test_request_user_set(self):
        user = User.objects.create(username="albertus_magnus")
        request = self.get_request(user)
        self.assertEqual(request.user, user)

    def test_request_user_is_none_working(self):
        request = self.get_request(None)
        self.assertEqual(request.user, None)

    def test_django_messages_set_up_correctly(self):
        request = self.get_request(None)

        # This would fail if the django messages were not set up correctly
        messages.add_message(request, messages.SUCCESS, "I am a great message!")

        self.assertIsInstance(request.session, SessionBase)

    def test_django_session_set_up_correctly(self):
        request = self.get_request(None)
        request.session["my_val"] = 27
        request.session.modified = True

        self.assertEqual(request.session["my_val"], 27)

    def test_passed_user_is_none(self):
        request = self.get_request(None)
        self.assertIsNone(request.user)

    def test_passed_user_is_regular_user(self):
        user = User.objects.create(username="albertus_magnus")
        request = self.get_request(user)
        self.assertEqual(request.user, user)

    def test_passed_user_is_anonymous_user(self):
        anonymous_user = AnonymousUser()
        request = self.get_request(anonymous_user)
        self.assertEqual(request.user, anonymous_user)

    def test_passed_user_is_other_type(self):
        wrong_object = MySingleSignalModel()
        with self.assertRaises(ValueError):
            self.get_request(wrong_object)

    def test_default_url_used(self):
        request = self.get_request()
        self.assertEqual(request.build_absolute_uri(), "http://testserver/")

    def test_passed_url_used(self):
        request = self.get_request(url="my-url")
        self.assertEqual(request.build_absolute_uri(), "http://testserver/my-url")

    def test_method_parameter_get(self):
        # Test that method parameter is set correctly for GET
        request = self.get_request(method="GET")
        self.assertEqual(request.method, "GET")

    def test_method_parameter_post(self):
        # Test that method parameter is set correctly for POST
        request = self.get_request(method="POST")
        self.assertEqual(request.method, "POST")

    def test_method_parameter_put(self):
        # Test that method parameter is set correctly for PUT
        request = self.get_request(method="PUT")
        self.assertEqual(request.method, "PUT")

    def test_method_parameter_delete(self):
        # Test that method parameter is set correctly for DELETE
        request = self.get_request(method="DELETE")
        self.assertEqual(request.method, "DELETE")

    def test_method_parameter_patch(self):
        # Test that method parameter is set correctly for PATCH
        request = self.get_request(method="PATCH")
        self.assertEqual(request.method, "PATCH")

    def test_combined_user_url_method(self):
        # Test combining all parameters
        user = User.objects.create(username="test_combined")
        request = self.get_request(user=user, method="POST", url="/test-url/")
        self.assertEqual(request.user, user)
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.build_absolute_uri(), "http://testserver/test-url/")
