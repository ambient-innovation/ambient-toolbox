from django.test import TestCase

from ambient_toolbox.permissions.fixtures.declarations import GroupPermissionDeclaration, PermissionModelDeclaration


class PermissionFixtureDeclarationTest(TestCase):
    def test_permission_model_declaration_regular(self):
        permission = PermissionModelDeclaration(
            app_label="my_app",
            codename_list=["view_mymodel"],
            model="mymodel",
        )

        self.assertEqual(permission.app_label, "my_app")
        self.assertEqual(permission.codename_list, ["view_mymodel"])
        self.assertEqual(permission.model, "mymodel")

    def test_group_permission_declaration_regular(self):
        permission = PermissionModelDeclaration(
            app_label="my_app",
            codename_list=["view_mymodel"],
            model="mymodel",
        )
        group = GroupPermissionDeclaration(
            name="my_group",
            permission_list=[permission],
        )

        self.assertEqual(group.name, "my_group")
        self.assertEqual(group.permission_list, [permission])
