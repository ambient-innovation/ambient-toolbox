from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase

from ambient_toolbox.admin.model_admins.inlines import ReadOnlyTabularInline
from ambient_toolbox.tests.mixins import RequestProviderMixin
from testapp.models import ForeignKeyRelatedModel, MySingleSignalModel


class TestReadOnlyTabularInline(ReadOnlyTabularInline):
    model = ForeignKeyRelatedModel


class AdminInlineTest(RequestProviderMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.super_user = User.objects.create(username="super_user", is_superuser=True)

    def test_read_only_tabular_inline_admin_all_fields_readonly(self):
        obj = MySingleSignalModel(value=1)
        fk_related_obj = ForeignKeyRelatedModel(single_signal=obj)

        admin_class = TestReadOnlyTabularInline(parent_model=MySingleSignalModel, admin_site=admin.site)
        readonly_fields = admin_class.get_readonly_fields(request=self.get_request(), obj=fk_related_obj)

        self.assertEqual(len(readonly_fields), 1)
        self.assertIn("single_signal", readonly_fields)

    def test_read_only_admin_tabular_inline_no_change_permissions(self):
        admin_class = TestReadOnlyTabularInline(parent_model=MySingleSignalModel, admin_site=admin.site)

        request = self.get_request(self.super_user)

        self.assertFalse(admin_class.has_add_permission(request))
        self.assertFalse(admin_class.has_change_permission(request))
        self.assertFalse(admin_class.has_delete_permission(request))
