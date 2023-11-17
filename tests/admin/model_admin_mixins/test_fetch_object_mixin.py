from unittest import mock

from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase

from ambient_toolbox.admin.model_admins.mixins import FetchObjectMixin
from ambient_toolbox.tests.mixins import RequestProviderMixin
from testapp.models import MySingleSignalModel


class TestFetchObjectMixinAdmin(FetchObjectMixin, admin.ModelAdmin):
    pass


class MockResolverResponse:
    kwargs = None


class FetchObjectMixinTest(RequestProviderMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.super_user = User.objects.create(username="super_user", is_superuser=True)

        admin.site.register(MySingleSignalModel, TestFetchObjectMixinAdmin)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        admin.site.unregister(MySingleSignalModel)

    def test_model_is_set(self):
        obj = MySingleSignalModel.objects.create(value=1)
        model_admin = TestFetchObjectMixinAdmin(model=MySingleSignalModel, admin_site=admin.site)

        request = self.get_request(self.super_user)

        return_obj = MockResolverResponse()
        return_obj.kwargs = {"object_id": obj.id}
        with mock.patch("ambient_toolbox.admin.model_admins.mixins.resolve", return_value=return_obj):
            obj_from_request = model_admin.get_object_from_request(request)

        self.assertEqual(obj_from_request, obj)
