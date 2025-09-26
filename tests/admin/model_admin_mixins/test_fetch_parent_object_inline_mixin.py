from unittest import mock

from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase

from ambient_toolbox.admin.model_admins.mixins import FetchParentObjectInlineMixin
from ambient_toolbox.tests.mixins import RequestProviderMixin
from testapp.models import ForeignKeyRelatedModel, MySingleSignalModel


class ForeignKeyRelatedModelTabularInline(FetchParentObjectInlineMixin, admin.TabularInline):
    model = ForeignKeyRelatedModel


class FetchParentObjectTestInlineMixinAdmin(admin.ModelAdmin):
    inlines = (ForeignKeyRelatedModelTabularInline,)


class MockResolverResponse:
    kwargs = None


class FetchParentObjectInlineMixinTest(RequestProviderMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.super_user = User.objects.create(username="super_user", is_superuser=True)

        admin.site.register(MySingleSignalModel, FetchParentObjectTestInlineMixinAdmin)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        admin.site.unregister(MySingleSignalModel)

    def test_parent_model_is_set(self):
        obj = MySingleSignalModel.objects.create(value=1)
        model_admin = FetchParentObjectTestInlineMixinAdmin(model=MySingleSignalModel, admin_site=admin.site)

        request = self.get_request(self.super_user)
        inline_list = model_admin.inlines

        self.assertGreater(len(inline_list), 0)

        inline = inline_list[0](parent_model=MySingleSignalModel, admin_site=admin.site)

        return_obj = MockResolverResponse()
        return_obj.kwargs = {"object_id": obj.id}
        with mock.patch.object(model_admin.inlines[0], "_resolve_url", return_value=return_obj):
            inline.get_formset(request=request, obj=obj)

        self.assertEqual(inline.parent_object, obj)

    def test_get_parent_object_from_request_returns_none_when_no_kwargs(self):
        """Test that get_parent_object_from_request returns None when resolved.kwargs is empty"""
        model_admin = FetchParentObjectTestInlineMixinAdmin(model=MySingleSignalModel, admin_site=admin.site)
        request = self.get_request(self.super_user)
        inline = model_admin.inlines[0](parent_model=MySingleSignalModel, admin_site=admin.site)

        return_obj = MockResolverResponse()
        return_obj.kwargs = None
        with mock.patch.object(model_admin.inlines[0], "_resolve_url", return_value=return_obj):
            result = inline.get_parent_object_from_request(request)

        self.assertIsNone(result)

    def test_resolve_url_method_coverage(self):
        """Test to ensure _resolve_url method is covered"""
        model_admin = FetchParentObjectTestInlineMixinAdmin(model=MySingleSignalModel, admin_site=admin.site)
        request = self.get_request(self.super_user)
        inline = model_admin.inlines[0](parent_model=MySingleSignalModel, admin_site=admin.site)

        # Call the actual _resolve_url method to cover line 56
        with mock.patch("ambient_toolbox.admin.model_admins.mixins.resolve") as mock_resolve:
            inline._resolve_url(request)
            mock_resolve.assert_called_once_with(request.path_info)
