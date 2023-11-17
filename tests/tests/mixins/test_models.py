from django.test import TestCase

from testapp.models import MyPermissionModelMixin


class PermissionModelMixinTest(TestCase):
    def test_meta_managed_false(self):
        self.assertFalse(MyPermissionModelMixin.Meta.managed)
