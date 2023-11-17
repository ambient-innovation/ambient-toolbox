from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.views import generic

from ambient_toolbox.admin.views.mixins import AdminViewMixin
from ambient_toolbox.tests.mixins import RequestProviderMixin
from testapp.models import MySingleSignalModel


class TestView(AdminViewMixin, generic.TemplateView):
    model = MySingleSignalModel
    admin_page_title = "My fancy title"
    template_name = "testapp/test_template.html"


class AdminViewMixinTest(RequestProviderMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.view = TestView()

        cls.super_user = User.objects.create(username="super_user", is_superuser=True)
        cls.regular_user = User.objects.create(username="test_user", is_superuser=False)

        # View needs a request since django 3.2
        request = cls.get_request(cls.super_user)
        cls.view.request = request

    def test_admin_view_mixin_has_view_permission_positive_case(self):
        self.assertTrue(self.view.has_view_permission(self.super_user))

    def test_admin_view_mixin_has_view_permission_negative_case(self):
        self.assertFalse(self.view.has_view_permission(self.regular_user))

    def test_admin_view_mixin_access_allowed_for_superusers(self):
        request = self.get_request(self.super_user)
        self.view.request = request

        self.view.dispatch(request=request)

    def test_admin_view_mixin_access_blocked_for_non_superusers(self):
        request = self.get_request(self.regular_user)

        with self.assertRaises(PermissionDenied):
            self.view.dispatch(request=request)

    def test_admin_view_mixin_get_admin_site_regular(self):
        self.assertIsInstance(self.view.get_admin_site(), AdminSite)

    def test_admin_view_mixin_get_context_data_regular(self):
        context_data = self.view.get_context_data()

        # Simply assert custom fields are available
        self.assertIn("site_header", context_data)
        self.assertIn("site_title", context_data)
        self.assertIn("name", context_data)
        self.assertIn("original", context_data)
        self.assertIn("is_nav_sidebar_enabled", context_data)
        self.assertIn("available_apps", context_data)
        self.assertIn("opts", context_data)
        self.assertIn("app_label", context_data["opts"])
        self.assertIn("verbose_name", context_data["opts"])
        self.assertIn("verbose_name_plural", context_data["opts"])
        self.assertIn("model_name", context_data["opts"])
        self.assertIn("app_config", context_data["opts"])
        self.assertIn("verbose_name", context_data["opts"]["app_config"])
        self.assertIn("has_permission", context_data)
