from django.contrib import admin
from django.contrib.auth.models import User
from django.forms import forms
from django.test import TestCase

from ambient_toolbox.admin.model_admins.mixins import AdminCreateFormMixin
from ambient_toolbox.tests.mixins import RequestProviderMixin
from testapp.models import ForeignKeyRelatedModel, MySingleSignalModel


class TestCreateForm(forms.Form):
    class Meta:
        custom_add_form = True


class TestAdminCreateFormMixinAdmin(AdminCreateFormMixin, admin.ModelAdmin):
    add_form = TestCreateForm


class AdminCreateFormMixinTest(RequestProviderMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.super_user = User.objects.create(username="super_user", is_superuser=True)

        admin.site.register(ForeignKeyRelatedModel, TestAdminCreateFormMixinAdmin)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        admin.site.unregister(ForeignKeyRelatedModel)

    def test_add_form_used_in_create_case(self):
        model_admin = TestAdminCreateFormMixinAdmin(model=ForeignKeyRelatedModel, admin_site=admin.site)

        form = model_admin.get_form(self.get_request(self.super_user))

        # Use Meta attribute from custom form class to determine if form was used. Base form is being wrapped
        # so we cannot assert the class.
        self.assertTrue(form.Meta.custom_add_form)

    def test_add_form_not_used_in_edit_case(self):
        model_admin = TestAdminCreateFormMixinAdmin(model=ForeignKeyRelatedModel, admin_site=admin.site)

        form = model_admin.get_form(
            self.get_request(self.super_user), obj=ForeignKeyRelatedModel(single_signal=MySingleSignalModel(value=1))
        )

        with self.assertRaises(AttributeError):
            self.assertFalse(form.Meta.custom_add_form)
