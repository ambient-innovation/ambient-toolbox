from django.test import TestCase

from testapp.models import MyPermissionModelMixin


class PermissionModelMixinTest(TestCase):
    def test_meta_managed_false(self):
        self.assertFalse(MyPermissionModelMixin.Meta.managed)

    def test_meta_no_default_permissions(self):
        self.assertEqual(len(MyPermissionModelMixin.Meta.default_permissions), 0)
