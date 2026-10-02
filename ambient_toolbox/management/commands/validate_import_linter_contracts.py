import sys

from django.core.management.base import BaseCommand

from ambient_toolbox.import_linter.services import ImportLinterContractService


class Command(BaseCommand):
    """
    Checks whether the import-linter contract file is still in sync with the current settings
    configuration and exits with a non-zero status when it is outdated.
    """

    help = "Validates that import-linter contracts are up to date."

    def handle(self, *args, **options):
        service = ImportLinterContractService()
        is_valid = service.validate_contracts()

        if is_valid:
            print("\033[32mImport-linter contracts successfully validated. Keep on importing.\033[0m")
        else:
            print(
                "\033[31mImport-linter contracts out of date! Please run "
                "'python manage.py update_import_linter_contracts'.\033[0m"
            )

        # 0 = success, 1 = error
        sys.exit(not is_valid)
