from django.test import TestCase

from ambient_toolbox.permissions.fixtures.helpers import generate_default_permissions


class PermissionFixtureHelperTest(TestCase):
    def test_generate_default_permissions_regular(self):
        permission_list = generate_default_permissions("mymodel")

        self.assertEqual(len(permission_list), 4)
        self.assertIn("add_mymodel", permission_list)
        self.assertIn("change_mymodel", permission_list)
        self.assertIn("delete_mymodel", permission_list)
        self.assertIn("view_mymodel", permission_list)
