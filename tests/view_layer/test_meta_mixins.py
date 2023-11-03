from unittest import mock

from django.contrib.auth.models import AnonymousUser, Permission, User
from django.http import HttpResponse
from django.test import TestCase
from django.views import generic

from ambient_toolbox.tests.mixins import RequestProviderMixin
from ambient_toolbox.view_layer.mixins import DjangoPermissionRequiredMixin


class MetaDjangoPermissionRequiredMixinTest(RequestProviderMixin, TestCase):
    class TestViewNoPerms(DjangoPermissionRequiredMixin, generic.View):
        pass

    class TestViewSinglePerm(DjangoPermissionRequiredMixin, generic.View):
        permission_list = ["auth.change_user"]
        login_view_name = "other-login-view"

        def get(self, *args, **kwargs):
            return HttpResponse(status=200)

    class TestViewMultiplePerms(DjangoPermissionRequiredMixin, generic.View):
        permission_list = ["auth.change_user", "auth.add_user"]

        def get_login_url(self):
            return "login/"

    class TestDifferentLoginNameView(DjangoPermissionRequiredMixin, generic.View):
        permission_list = ["auth.change_user"]
        login_view_name = "other-login-view"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.permission = Permission.objects.get_by_natural_key(app_label="auth", codename="change_user", model="user")

    def setUp(self) -> None:
        super().setUp()
        self.user = User.objects.create(username="test_user", email="test.user@ambient-toolbox.com")

    def test_get_login_url(self):
        self.assertEqual(self.TestViewMultiplePerms().get_login_url(), "login/")

    def test_get_custom_login_url(self):
        self.assertEqual(self.TestDifferentLoginNameView().get_login_url(), "/other/login/")

    def test_permissions_are_set_validation(self):
        with self.assertRaises(RuntimeError):
            self.TestViewNoPerms()

    def test_has_permissions_correct_permission(self):
        self.user.user_permissions.add(self.permission)

        self.assertTrue(self.TestViewSinglePerm().has_permissions(self.user))

    def test_has_permissions_missing_permission(self):
        self.assertFalse(self.TestViewSinglePerm().has_permissions(self.user))

    def test_has_permissions_multiple_permissions_one_missing(self):
        self.user.user_permissions.add(self.permission)

        self.assertFalse(self.TestViewMultiplePerms().has_permissions(self.user))

    def test_passes_login_barrier_no_login_required(self):
        view = self.TestViewSinglePerm()
        view.login_required = False

        self.assertTrue(view.passes_login_barrier(self.user))

    def test_passes_login_barrier_user_logged_in(self):
        self.assertTrue(self.TestViewSinglePerm().passes_login_barrier(self.user))

    def test_passes_login_barrier_user_not_logged_in(self):
        self.assertFalse(self.TestViewSinglePerm().passes_login_barrier(AnonymousUser()))

    def test_has_permissions_is_superuser_is_not_blocked(self):
        self.user.is_superuser = True
        self.assertTrue(self.TestViewSinglePerm().has_permissions(self.user))

    def test_has_permissions_django_superuser_is_always_allowed(self):
        self.user.is_superuser = True
        self.assertTrue(self.TestViewSinglePerm().has_permissions(self.user))

    @mock.patch.object(TestViewSinglePerm, "passes_login_barrier", return_value=True)
    @mock.patch.object(TestViewSinglePerm, "has_permissions", return_value=True)
    def test_dispatch_regular(self, *args):
        response = self.TestViewSinglePerm().dispatch(request=self.get_request(self.user))

        self.assertEqual(response.status_code, 200)

    def test_dispatch_lockout_on_missing_permissions(self):
        response = self.TestViewSinglePerm().dispatch(request=self.get_request(self.user))

        self.assertEqual(response.status_code, 403)

    def test_dispatch_working_on_having_permissions(self):
        self.user.user_permissions.add(self.permission)
        view = self.TestViewSinglePerm()
        response = view.dispatch(request=self.get_request(self.user))

        self.assertEqual(response.status_code, 200)

    @mock.patch.object(TestViewSinglePerm, "passes_login_barrier", return_value=False)
    def test_dispatch_passes_login_barrier_false(self, *args):
        view = self.TestViewSinglePerm()
        response = view.dispatch(request=self.get_request(self.user))

        self.assertEqual(response.status_code, 302)
