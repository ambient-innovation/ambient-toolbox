from unittest import mock

from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase

from ambient_toolbox.admin.model_admins.mixins import CommonInfoAdminMixin
from ambient_toolbox.tests.mixins import RequestProviderMixin
from testapp.models import CommonInfoBasedModel


class CommonInfoBasedModelForm(forms.ModelForm):
    class Meta:
        model = CommonInfoBasedModel
        fields = ("value",)


class TestCommonInfoAdminMixinAdmin(CommonInfoAdminMixin, admin.ModelAdmin):
    pass


class CommonInfoAdminMixinTest(RequestProviderMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = User.objects.create(username="my_user")
        cls.request = cls.get_request(cls.user)

        admin.site.register(CommonInfoBasedModel, TestCommonInfoAdminMixinAdmin)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        admin.site.unregister(CommonInfoBasedModel)

    def test_readonly_fields_are_set(self):
        model_admin = TestCommonInfoAdminMixinAdmin(model=CommonInfoBasedModel, admin_site=admin.site)

        self.assertIn("created_by", model_admin.get_readonly_fields(self.request))
        self.assertIn("created_at", model_admin.get_readonly_fields(self.request))

        self.assertIn("lastmodified_by", model_admin.get_readonly_fields(self.request))
        self.assertIn("lastmodified_at", model_admin.get_readonly_fields(self.request))

    def test_get_user_obj_regular(self):
        model_admin = TestCommonInfoAdminMixinAdmin(model=CommonInfoBasedModel, admin_site=admin.site)

        self.assertEqual(self.request.user, model_admin.get_user_obj(request=self.request))

    def test_created_by_is_set_on_creation(self):
        model_admin = TestCommonInfoAdminMixinAdmin(model=CommonInfoBasedModel, admin_site=admin.site)

        obj = model_admin.save_form(self.request, CommonInfoBasedModelForm(), False)

        self.assertEqual(obj.created_by, self.user)
        self.assertEqual(obj.lastmodified_by, self.user)

    def test_created_by_is_not_altered_on_update(self):
        model_admin = TestCommonInfoAdminMixinAdmin(model=CommonInfoBasedModel, admin_site=admin.site)

        other_user = User.objects.create(username="other_user")
        with mock.patch.object(CommonInfoBasedModel, "get_current_user", return_value=other_user):
            obj = CommonInfoBasedModel.objects.create(value=1, created_by=other_user, lastmodified_by=other_user)

        form = CommonInfoBasedModelForm(instance=obj)
        obj = model_admin.save_form(self.request, form, True)

        self.assertEqual(obj.created_by, other_user)
        self.assertEqual(obj.lastmodified_by, self.user)
