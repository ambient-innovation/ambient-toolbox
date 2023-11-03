from unittest import mock

from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase

from ambient_toolbox.admin.model_admins.mixins import FetchParentObjectInlineMixin
from ambient_toolbox.tests.mixins import RequestProviderMixin
from testapp.models import ForeignKeyRelatedModel, MySingleSignalModel


class ForeignKeyRelatedModelTabularInline(FetchParentObjectInlineMixin, admin.TabularInline):
    model = ForeignKeyRelatedModel


class TestFetchParentObjectInlineMixinAdmin(admin.ModelAdmin):
    inlines = (ForeignKeyRelatedModelTabularInline,)


class MockResolverResponse:
    kwargs = None


class FetchParentObjectInlineMixinTest(RequestProviderMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.super_user = User.objects.create(username="super_user", is_superuser=True)

        admin.site.register(MySingleSignalModel, TestFetchParentObjectInlineMixinAdmin)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        admin.site.unregister(MySingleSignalModel)

    def test_parent_model_is_set(self):
        obj = MySingleSignalModel.objects.create(value=1)
        model_admin = TestFetchParentObjectInlineMixinAdmin(model=MySingleSignalModel, admin_site=admin.site)

        request = self.get_request(self.super_user)
        inline_list = model_admin.inlines

        self.assertGreater(len(inline_list), 0)

        inline = inline_list[0](parent_model=MySingleSignalModel, admin_site=admin.site)

        return_obj = MockResolverResponse()
        return_obj.kwargs = {"object_id": obj.id}
        with mock.patch.object(model_admin.inlines[0], "_resolve_url", return_value=return_obj):
            inline.get_formset(request=request, obj=obj)

        self.assertEqual(inline.parent_object, obj)
