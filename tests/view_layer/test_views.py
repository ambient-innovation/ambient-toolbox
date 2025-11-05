from unittest import mock
from unittest.mock import Mock

from django.contrib.auth.models import User
from django.test import TestCase
from django.views import generic
from django.views.defaults import ERROR_403_TEMPLATE_NAME
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

from ambient_toolbox.tests.mixins import RequestProviderMixin
from ambient_toolbox.view_layer.views import (
    CustomPermissionMixin,
    RequestInFormKwargsMixin,
    ToggleView,
)
from testapp.views import UserInFormKwargsMixinView


class CustomPermissionMixinTest(RequestProviderMixin, TestCase):
    """Test suite for CustomPermissionMixin."""

    class TestView(CustomPermissionMixin, generic.View):
        """Test view that uses CustomPermissionMixin."""

        def get(self, request, *args, **kwargs):
            return Mock(content="Success")

    class TestViewWithPermissionDenied(CustomPermissionMixin, generic.View):
        """Test view that denies permissions."""

        def validate_permissions(self):
            return False

        def get(self, request, *args, **kwargs):
            return Mock(content="Success")

    def test_validate_permissions_default_returns_true(self):
        """Test that validate_permissions() returns True by default."""
        view = self.TestView()
        self.assertTrue(view.validate_permissions())

    @mock.patch.object(generic.View, "dispatch", return_value=Mock(content="Success"))
    def test_dispatch_with_permission_granted_calls_super(self, mock_dispatch):
        """Test that dispatch() calls super().dispatch() when permissions are granted."""
        view = self.TestView()
        request = self.get_request()

        response = view.dispatch(request)
        mock_dispatch.assert_called_once_with(request)
        self.assertEqual(response.content, "Success")

    @mock.patch("ambient_toolbox.view_layer.views.render")
    def test_dispatch_with_permission_denied_returns_403(self, mock_render):
        """Test that dispatch() returns 403 when permissions are denied."""
        view = self.TestViewWithPermissionDenied()
        request = self.get_request()
        view.request = request

        mock_render.return_value = Mock(status_code=403)
        response = view.dispatch(request)

        mock_render.assert_called_once_with(request, ERROR_403_TEMPLATE_NAME, status=403)
        self.assertEqual(response.status_code, 403)


class RequestInFormKwargsMixinTest(RequestProviderMixin, TestCase):
    """Test suite for RequestInFormKwargsMixin."""

    class TestView(RequestInFormKwargsMixin, generic.FormView):
        """Test view that uses RequestInFormKwargsMixin."""


    def test_get_form_kwargs_adds_request(self):
        """Test that get_form_kwargs() adds request to kwargs."""
        user = User(username="test-user")
        view = self.TestView()
        view.request = self.get_request(user=user)
        form_kwargs = view.get_form_kwargs()

        self.assertIn("request", form_kwargs)
        self.assertEqual(form_kwargs["request"], view.request)

    def test_get_form_kwargs_calls_super(self):
        """Test that get_form_kwargs() properly calls super()."""
        user = User(username="test-user")
        view = self.TestView()
        view.request = self.get_request(user=user)
        form_kwargs = view.get_form_kwargs()

        # Check that super() was called by verifying standard kwargs are present
        self.assertIn("request", form_kwargs)


class UserInFormKwargsMixinTest(RequestProviderMixin, TestCase):
    """Test suite for UserInFormKwargsMixin."""

    def test_get_form_kwargs_adds_user(self):
        """Test that get_form_kwargs() adds user to kwargs."""
        user = User(username="my-user")

        view = UserInFormKwargsMixinView()
        view.request = self.get_request(user=user)
        form_kwargs = view.get_form_kwargs()

        self.assertIn("user", form_kwargs)
        self.assertEqual(form_kwargs["user"], user)

    def test_get_form_kwargs_calls_super(self):
        """Test that get_form_kwargs() properly calls super()."""
        user = User(username="test-user")
        view = UserInFormKwargsMixinView()
        view.request = self.get_request(user=user)
        form_kwargs = view.get_form_kwargs()

        # Check that super() was called by verifying standard kwargs are present
        self.assertIn("user", form_kwargs)


class ToggleViewTest(RequestProviderMixin, TestCase):
    """Test suite for ToggleView."""

    def test_http_method_set_correctly(self):
        """Test that http_method_names is set to only POST."""
        self.assertEqual(ToggleView.http_method_names, ("post",))

    def test_post_raises_not_implemented_error(self):
        """Test that post() raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            view = ToggleView()
            view.post(request=self.get_request())

    def test_class_inherits_from_single_object_mixin(self):
        """Test that ToggleView inherits from SingleObjectMixin."""
        self.assertTrue(issubclass(ToggleView, SingleObjectMixin))

    def test_class_inherits_from_generic_view(self):
        """Test that ToggleView inherits from generic.View."""
        self.assertTrue(issubclass(ToggleView, View))
