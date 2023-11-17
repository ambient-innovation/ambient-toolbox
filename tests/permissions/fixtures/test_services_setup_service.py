from django.contrib.auth.models import Group, Permission
from django.test import TestCase

from ambient_toolbox.permissions.fixtures.declarations import GroupPermissionDeclaration, PermissionModelDeclaration
from ambient_toolbox.permissions.fixtures.services import PermissionSetupService


class PermissionSetupServiceTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.group, created = Group.objects.get_or_create(name="my_group")

        cls.permission_view = Permission.objects.get_by_natural_key(
            app_label="testapp", codename="view_mysinglesignalmodel", model="mysinglesignalmodel"
        )
        cls.permission_change = Permission.objects.get_by_natural_key(
            app_label="testapp", codename="change_mysinglesignalmodel", model="mysinglesignalmodel"
        )

    def test_init_regular(self):
        group_declaration = GroupPermissionDeclaration(name="my_group", permission_list=[])
        service = PermissionSetupService(group_declaration=group_declaration)

        self.assertEqual(service.group_declaration, group_declaration)
        self.assertFalse(service.dry_run)

    def test_process_add_permission(self):
        group_declaration = GroupPermissionDeclaration(
            name="my_group",
            permission_list=[
                PermissionModelDeclaration(
                    app_label="testapp", codename_list=["change_mysinglesignalmodel"], model="mysinglesignalmodel"
                )
            ],
        )

        service = PermissionSetupService(group_declaration=group_declaration)
        new_permissions, removed_permissions = service.process()

        self.assertEqual(new_permissions, [self.permission_change])
        self.assertEqual(removed_permissions, [])

        self.group.refresh_from_db()
        self.assertEqual(self.group.permissions.count(), 1)
        self.assertEqual(self.group.permissions.all().first(), self.permission_change)

    def test_process_remove_permission(self):
        self.group.permissions.add(self.permission_view)

        group_declaration = GroupPermissionDeclaration(name="my_group", permission_list=[])

        service = PermissionSetupService(group_declaration=group_declaration)
        new_permissions, removed_permissions = service.process()

        self.assertEqual(new_permissions, [])
        self.assertEqual(removed_permissions, [self.permission_view])

        self.group.refresh_from_db()
        self.assertFalse(self.group.permissions.exists())

    def test_process_no_changes_permission(self):
        self.group.permissions.add(self.permission_view)

        group_declaration = GroupPermissionDeclaration(
            name="my_group",
            permission_list=[
                PermissionModelDeclaration(
                    app_label="testapp", codename_list=["view_mysinglesignalmodel"], model="mysinglesignalmodel"
                )
            ],
        )

        service = PermissionSetupService(group_declaration=group_declaration)
        new_permissions, removed_permissions = service.process()

        self.assertEqual(new_permissions, [])
        self.assertEqual(removed_permissions, [])

        self.group.refresh_from_db()
        self.assertEqual(self.group.permissions.count(), 1)
        self.assertEqual(self.group.permissions.all().first(), self.permission_view)

    def test_process_invalid_permission(self):
        self.group.permissions.add(self.permission_view)

        group_declaration = GroupPermissionDeclaration(
            name="my_group",
            permission_list=[
                PermissionModelDeclaration(
                    app_label="testapp", codename_list=["invalid_permission"], model="mysinglesignalmodel"
                )
            ],
        )

        service = PermissionSetupService(group_declaration=group_declaration)
        with self.assertRaisesMessage(
            ValueError, 'Invalid permission "mysinglesignalmodel.invalid_permission" declared.'
        ):
            service.process()

    def test_process_invalid_app(self):
        self.group.permissions.add(self.permission_view)

        group_declaration = GroupPermissionDeclaration(
            name="my_group",
            permission_list=[
                PermissionModelDeclaration(
                    app_label="invalid_app", codename_list=["view_mysinglesignalmodel"], model="mysinglesignalmodel"
                )
            ],
        )

        service = PermissionSetupService(group_declaration=group_declaration)
        with self.assertRaisesMessage(ValueError, 'Invalid content type "invalid_app.mysinglesignalmodel" declared.'):
            service.process()

    def test_process_invalid_model(self):
        self.group.permissions.add(self.permission_view)

        group_declaration = GroupPermissionDeclaration(
            name="my_group",
            permission_list=[
                PermissionModelDeclaration(
                    app_label="testapp", codename_list=["view_mysinglesignalmodel"], model="invalid_model"
                )
            ],
        )

        service = PermissionSetupService(group_declaration=group_declaration)
        with self.assertRaisesMessage(ValueError, 'Invalid content type "testapp.invalid_model" declared.'):
            service.process()

    def test_process_duplicated_permission_declaration(self):
        self.group.permissions.add(self.permission_view)

        group_declaration = GroupPermissionDeclaration(
            name="my_group",
            permission_list=[
                PermissionModelDeclaration(
                    app_label="testapp", codename_list=["view_mysinglesignalmodel"], model="mysinglesignalmodel"
                ),
                PermissionModelDeclaration(
                    app_label="testapp", codename_list=["view_mysinglesignalmodel"], model="mysinglesignalmodel"
                ),
            ],
        )

        service = PermissionSetupService(group_declaration=group_declaration)
        with self.assertRaisesMessage(ValueError, f"Permission {self.permission_view} declared twice."):
            service.process()

    def test_process_dry_run_not_persisting(self):
        self.group.permissions.add(self.permission_view)

        group_declaration = GroupPermissionDeclaration(
            name="my_group",
            permission_list=[
                PermissionModelDeclaration(
                    app_label="testapp", codename_list=["change_mysinglesignalmodel"], model="mysinglesignalmodel"
                )
            ],
        )

        service = PermissionSetupService(group_declaration=group_declaration, dry_run=True)
        new_permissions, removed_permissions = service.process()

        self.assertEqual(new_permissions, [self.permission_change])
        self.assertEqual(removed_permissions, [self.permission_view])

        self.group.refresh_from_db()
        self.assertEqual(self.group.permissions.count(), 1)
        self.assertEqual(self.group.permissions.all().first(), self.permission_view)
