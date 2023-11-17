from unittest import mock

from django.contrib import admin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.test import TestCase

from ambient_toolbox.admin.model_admins.mixins import DeactivatableChangeViewAdminMixin
from ambient_toolbox.tests.mixins import RequestProviderMixin


class TestAdmin(DeactivatableChangeViewAdminMixin, admin.ModelAdmin):
    pass


class DeactivatableChangeViewAdminMixinTest(RequestProviderMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Use random model for this meta test
        cls.user = User.objects.create(username="test_user", is_superuser=False)
        cls.super_user = User.objects.create(username="super_user", is_superuser=True)

    def test_can_see_change_view_positive_flag(self):
        admin_cls = TestAdmin(admin_site=None, model=User)
        self.assertTrue(admin_cls.can_see_change_view(request=self.get_request()))

    def test_can_see_change_view_negative_flag(self):
        admin_cls = TestAdmin(admin_site=None, model=User)
        admin_cls.enable_change_view = False
        self.assertFalse(admin_cls.can_see_change_view(request=self.get_request()))

    def test_get_list_display_links_can_see_method_called(self):
        admin_cls = TestAdmin(admin_site=None, model=User)
        with mock.patch.object(admin_cls, "can_see_change_view", return_value=True) as mock_method:
            admin_cls.get_list_display_links(request=self.get_request(user=self.user), list_display=("first_name",))

        mock_method.assert_called_once()

    def test_get_list_display_links_can_see_method_positive_flag(self):
        admin_cls = TestAdmin(admin_site=None, model=User)
        field_tuple = ("first_name",)
        self.assertEqual(
            list(field_tuple),
            admin_cls.get_list_display_links(request=self.get_request(user=self.user), list_display=field_tuple),
        )

    def test_get_list_display_links_can_see_method_negative_flag(self):
        admin_cls = TestAdmin(admin_site=None, model=User)
        admin_cls.enable_change_view = False
        self.assertIsNone(
            admin_cls.get_list_display_links(request=self.get_request(user=self.user), list_display=("first_name",))
        )

    def test_change_view_can_see_method_called_because_of_positive_flag(self):
        admin_cls = TestAdmin(admin_site=None, model=User)
        with mock.patch.object(admin_cls, "can_see_change_view", return_value=True) as mocked_can_see_method:
            with mock.patch("django.contrib.admin.ModelAdmin.change_view") as mocked_base_change_view:
                admin_cls.change_view(request=self.get_request(user=self.super_user), object_id=str(self.user.id))

        mocked_can_see_method.assert_called_once()
        mocked_base_change_view.assert_called_once()

    def test_change_view_can_see_method_not_called_because_of_negative_flag(self):
        admin_cls = TestAdmin(admin_site=None, model=User)
        with mock.patch.object(admin_cls, "can_see_change_view", return_value=False) as mocked_can_see_method:
            with mock.patch("django.contrib.admin.ModelAdmin.change_view") as mocked_base_change_view:
                admin_cls.change_view(request=self.get_request(user=self.super_user), object_id=str(self.user.id))

        mocked_can_see_method.assert_called_once()
        mocked_base_change_view.assert_not_called()

    def test_change_view_can_see_method_not_called_but_redirect(self):
        admin_cls = TestAdmin(admin_site=None, model=User)
        admin_cls.enable_change_view = False
        result = admin_cls.change_view(request=self.get_request(user=self.super_user), object_id=str(self.user.id))

        self.assertIsInstance(result, HttpResponseRedirect)
