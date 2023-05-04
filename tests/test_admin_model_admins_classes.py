from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase

from ambient_toolbox.admin.model_admins.classes import EditableOnlyAdmin, ReadOnlyAdmin
from ambient_toolbox.tests.mixins import RequestProviderMixin
from testapp.models import MyMultipleSignalModel, MySingleSignalModel


class TestReadOnlyAdmin(ReadOnlyAdmin):
    pass


class TestEditableOnlyAdmin(EditableOnlyAdmin):
    pass


class AdminClassesTest(RequestProviderMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.super_user = User.objects.create(username='super_user', is_superuser=True)

        admin.site.register(MySingleSignalModel, TestReadOnlyAdmin)
        admin.site.register(MyMultipleSignalModel, TestEditableOnlyAdmin)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        admin.site.unregister(MySingleSignalModel)
        admin.site.unregister(MyMultipleSignalModel)

    def test_read_only_admin_all_fields_readonly(self):
        obj = MySingleSignalModel(value=1)

        admin_class = TestReadOnlyAdmin(model=obj, admin_site=admin.site)
        readonly_fields = admin_class.get_readonly_fields(request=self.get_request(), obj=obj)

        self.assertEqual(len(readonly_fields), 2)
        self.assertIn('id', readonly_fields)
        self.assertIn('value', readonly_fields)

    def test_read_only_admin_no_change_permissions(self):
        admin_class = TestReadOnlyAdmin(model=MySingleSignalModel, admin_site=admin.site)

        request = self.get_request(self.super_user)

        self.assertFalse(admin_class.has_add_permission(request))
        self.assertFalse(admin_class.has_change_permission(request))
        self.assertFalse(admin_class.has_delete_permission(request))

    def test_editable_only_admin_delete_action_removed(self):
        obj = MyMultipleSignalModel(value=1)
        admin_class = TestEditableOnlyAdmin(model=obj, admin_site=admin.site)

        request = self.get_request(self.super_user)
        actions = admin_class.get_actions(request=request)

        self.assertNotIn('delete_selected', actions)

    def test_editable_only_admin_no_change_permissions(self):
        admin_class = TestEditableOnlyAdmin(model=MyMultipleSignalModel, admin_site=admin.site)

        request = self.get_request(self.super_user)

        self.assertTrue(admin_class.has_change_permission(request))

        self.assertFalse(admin_class.has_add_permission(request))
        self.assertFalse(admin_class.has_delete_permission(request))
