from typing import List

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from ambient_toolbox.permissions.fixtures.declarations import GroupPermissionDeclaration


class PermissionSetupService:
    group_declaration: GroupPermissionDeclaration
    dry_run: bool

    def __init__(self, group_declaration: GroupPermissionDeclaration, dry_run: bool = False) -> None:
        super().__init__()

        self.group_declaration = group_declaration
        self.dry_run = dry_run

    @transaction.atomic
    def process(self) -> (List[Permission], List[Permission]):
        # Fetch or create group
        group, created = Group.objects.get_or_create(name=self.group_declaration.name)

        # Declare lists where we'll sort in the permissions
        defined_permission_list = []
        new_permissions = []
        removed_permissions = []

        # Iterate all in fixtures defined permission models...
        for permission_declaration in self.group_declaration.permission_list:
            # Iterate all fixture permissions...
            for codename in permission_declaration.codename_list:
                # Instantiate permission as ORM object
                try:
                    # Cast strings to lower cases to avoid issues with SQLite
                    new_permission = Permission.objects.get_by_natural_key(
                        app_label=permission_declaration.app_label.lower(),
                        codename=codename.lower(),
                        model=permission_declaration.model.lower(),
                    )
                except Permission.DoesNotExist as e:
                    raise ValueError(f'Invalid permission "{permission_declaration.model}.{codename}" declared.') from e
                except ContentType.DoesNotExist as e:
                    raise ValueError(
                        f'Invalid content type "{permission_declaration.app_label}'
                        f'.{permission_declaration.model}" declared.'
                    ) from e

                # Add permission object to list
                if new_permission in defined_permission_list:
                    raise ValueError(f"Permission {new_permission} declared twice.")
                defined_permission_list.append(new_permission)

                # Check if permission is already set in the group
                if new_permission not in group.permissions.all():
                    new_permissions.append(new_permission)

        # Check which permissions were removed for the given group
        for existing_permission in group.permissions.all():
            if existing_permission not in defined_permission_list:
                removed_permissions.append(existing_permission)  # noqa: PERF401

        if not self.dry_run:
            # Persist changes on removed permissions
            if len(removed_permissions):
                group.permissions.remove(*removed_permissions)

            # Persist changes on added permissions
            if len(new_permissions):
                group.permissions.add(*new_permissions)

        # Return changes
        return new_permissions, removed_permissions
