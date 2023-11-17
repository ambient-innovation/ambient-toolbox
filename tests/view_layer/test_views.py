from django.contrib.auth.models import User
from django.test import TestCase
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

from ambient_toolbox.tests.mixins import RequestProviderMixin
from ambient_toolbox.view_layer.views import ToggleView
from testapp.views import UserInFormKwargsMixinView


class UserInFormKwargsMixinTest(RequestProviderMixin, TestCase):
    def test_get_form_kwargs_regular(self):
        user = User(username="my-user")

        view = UserInFormKwargsMixinView()
        view.request = self.get_request(user=user)
        form_kwargs = view.get_form_kwargs()

        self.assertIn("user", form_kwargs)
        self.assertEqual(form_kwargs["user"], user)


class ToggleViewTest(RequestProviderMixin, TestCase):
    def test_http_method_set_correctly(self):
        self.assertEqual(ToggleView.http_method_names, ("post",))

    def test_post_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            view = ToggleView()
            view.post(request=self.get_request())

    def test_class_inherits_from_single_object_mixin(self):
        self.assertTrue(issubclass(ToggleView, SingleObjectMixin))

    def test_class_inherits_from_generic_view(self):
        self.assertTrue(issubclass(ToggleView, View))
