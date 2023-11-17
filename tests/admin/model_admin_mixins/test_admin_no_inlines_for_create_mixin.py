from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase

from ambient_toolbox.admin.model_admins.mixins import AdminNoInlinesForCreateMixin
from ambient_toolbox.tests.mixins import RequestProviderMixin
from testapp.models import ForeignKeyRelatedModel, MySingleSignalModel


class ForeignKeyRelatedModelTabularInline(admin.TabularInline):
    model = ForeignKeyRelatedModel


class TestAdminNoInlinesForCreateMixinAdmin(AdminNoInlinesForCreateMixin, admin.ModelAdmin):
    inlines = (ForeignKeyRelatedModelTabularInline,)


class AdminNoInlinesForCreateMixinTest(RequestProviderMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.super_user = User.objects.create(username="super_user", is_superuser=True)

        admin.site.register(MySingleSignalModel, TestAdminNoInlinesForCreateMixinAdmin)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        admin.site.unregister(MySingleSignalModel)

    def test_inlines_are_removed_on_create(self):
        model_admin = TestAdminNoInlinesForCreateMixinAdmin(model=MySingleSignalModel, admin_site=admin.site)

        self.assertEqual(model_admin.get_inline_instances(self.get_request(self.super_user), obj=None), [])

    def test_inlines_are_not_removed_on_edit(self):
        model_admin = TestAdminNoInlinesForCreateMixinAdmin(model=MySingleSignalModel, admin_site=admin.site)

        self.assertEqual(
            len(model_admin.get_inline_instances(self.get_request(self.super_user), obj=MySingleSignalModel(value=1))),
            1,
        )
