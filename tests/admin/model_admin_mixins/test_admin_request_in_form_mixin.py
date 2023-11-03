from django.contrib import admin
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase

from ambient_toolbox.admin.model_admins.mixins import AdminRequestInFormMixin
from ambient_toolbox.tests.mixins import RequestProviderMixin
from testapp.models import MySingleSignalModel


class TestAdminRequestInFormMixinAdmin(AdminRequestInFormMixin, admin.ModelAdmin):
    pass


class AdminRequestInFormMixinTest(RequestProviderMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.super_user = User.objects.create(username="super_user", is_superuser=True)

        admin.site.register(MySingleSignalModel, TestAdminRequestInFormMixinAdmin)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        admin.site.unregister(MySingleSignalModel)

    def test_request_is_in_form(self):
        model_admin = TestAdminRequestInFormMixinAdmin(model=MySingleSignalModel, admin_site=admin.site)
        form = model_admin.get_form(self.get_request(self.super_user))

        self.assertIsInstance(form.request, HttpRequest)
