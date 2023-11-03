from pydoc import locate

from django.conf import settings
from django.core.management.base import BaseCommand

from ambient_toolbox.permissions.fixtures.declarations import GroupPermissionDeclaration
from ambient_toolbox.permissions.fixtures.services import PermissionSetupService


class Command(BaseCommand):
    help = "Installs Ambient toolbox improved group permission fixtures"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Doesn't persist any changes in the database",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run")
        if dry_run:
            print('Starting in "dry-run" mode...')

        try:
            fixture_declaration_list = settings.GROUP_PERMISSION_FIXTURES
        except AttributeError:
            print("No fixtures found in Django settings.")
            fixture_declaration_list = []

        for declaration_path in fixture_declaration_list:
            print(f'Reading fixture declaration "{declaration_path}"...')
            declaration_class: GroupPermissionDeclaration = locate(declaration_path)

            assert isinstance(
                declaration_class, type(GroupPermissionDeclaration)
            ), f'Could\'t load group declaration "{declaration_path}".'

            print(f'> Installing permissions of group "{declaration_class.name}"...')
            service = PermissionSetupService(group_declaration=declaration_class, dry_run=dry_run)
            new_permissions, removed_permissions = service.process()

            print(f"> Newly installed permissions: {new_permissions}")
            print(f"> Removed permissions: {removed_permissions}\n")
