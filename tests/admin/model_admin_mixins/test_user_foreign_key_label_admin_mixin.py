from unittest import mock

from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase

from ambient_toolbox.admin.model_admins.mixins import UserForeignKeyLabelAdminMixin
from ambient_toolbox.tests.mixins import RequestProviderMixin
from testapp.models import ForeignKeyRelatedModel, ModelWithM2MToUser, ModelWithoutRelatedNameOnFieldAndMeta


class UserForeignKeyLabelTestAdmin(UserForeignKeyLabelAdminMixin, admin.ModelAdmin):
    pass


class UserForeignKeyLabelAdminMixinTest(RequestProviderMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = User.objects.create(username="my_user", first_name="Jane", last_name="Doe", email="jane@example.com")
        cls.request = cls.get_request(cls.user)

        admin.site.register(ModelWithoutRelatedNameOnFieldAndMeta, UserForeignKeyLabelTestAdmin)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        admin.site.unregister(ModelWithoutRelatedNameOnFieldAndMeta)

    def test_foreignkey_label_is_overridden_for_user(self):
        model_admin = UserForeignKeyLabelTestAdmin(model=ModelWithoutRelatedNameOnFieldAndMeta, admin_site=admin.site)
        db_field = ModelWithoutRelatedNameOnFieldAndMeta._meta.get_field("relation_field")
        formfield = model_admin.formfield_for_foreignkey(db_field, self.request)

        self.assertEqual(formfield.label_from_instance(self.user), "Jane Doe (jane@example.com)")

    def test_foreignkey_label_uses_get_label_for_user(self):
        model_admin = UserForeignKeyLabelTestAdmin(model=ModelWithoutRelatedNameOnFieldAndMeta, admin_site=admin.site)
        model_admin.get_label_for_user = mock.Mock(return_value="Custom Label")

        db_field = ModelWithoutRelatedNameOnFieldAndMeta._meta.get_field("relation_field")
        formfield = model_admin.formfield_for_foreignkey(db_field, self.request)

        self.assertEqual(formfield.label_from_instance(self.user), "Custom Label")

    def test_get_label_for_user_default(self):
        model_admin = UserForeignKeyLabelTestAdmin(model=ModelWithoutRelatedNameOnFieldAndMeta, admin_site=admin.site)
        label = model_admin.get_label_for_user(self.user)
        self.assertEqual(label, "Jane Doe (jane@example.com)")

    def test_manytomany_label_is_overridden_for_user(self):
        model_admin = UserForeignKeyLabelTestAdmin(model=ModelWithM2MToUser, admin_site=admin.site)
        db_field = ModelWithM2MToUser._meta.get_field("users")
        formfield = model_admin.formfield_for_manytomany(db_field, self.request)

        self.assertEqual(formfield.label_from_instance(self.user), "Jane Doe (jane@example.com)")

    def test_foreignkey_returns_none_formfield_gracefully(self):
        """Ensure None formfield (e.g. hidden field) is handled without error."""
        model_admin = UserForeignKeyLabelTestAdmin(model=ModelWithoutRelatedNameOnFieldAndMeta, admin_site=admin.site)
        db_field = ModelWithoutRelatedNameOnFieldAndMeta._meta.get_field("relation_field")

        with mock.patch.object(admin.ModelAdmin, "formfield_for_foreignkey", return_value=None):
            result = model_admin.formfield_for_foreignkey(db_field, self.request)

        self.assertIsNone(result)

    def test_manytomany_returns_none_formfield_gracefully(self):
        """Ensure None formfield from super is handled without error."""
        model_admin = UserForeignKeyLabelTestAdmin(model=ModelWithM2MToUser, admin_site=admin.site)
        db_field = ModelWithM2MToUser._meta.get_field("users")

        with mock.patch.object(admin.ModelAdmin, "formfield_for_manytomany", return_value=None):
            result = model_admin.formfield_for_manytomany(db_field, self.request)

        self.assertIsNone(result)

    def test_non_user_foreignkey_is_not_affected(self):
        """Ensure FK fields not pointing to User are left untouched."""

        class FKRelatedTestAdmin(UserForeignKeyLabelAdminMixin, admin.ModelAdmin):
            pass

        model_admin = FKRelatedTestAdmin(model=ForeignKeyRelatedModel, admin_site=admin.site)
        db_field = ForeignKeyRelatedModel._meta.get_field("single_signal")
        formfield = model_admin.formfield_for_foreignkey(db_field, self.request)

        # label_from_instance should NOT be overridden for non-User FK
        self.assertNotEqual(formfield.label_from_instance, model_admin.get_label_for_user)
