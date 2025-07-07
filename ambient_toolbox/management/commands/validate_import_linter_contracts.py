import sys

from django.core.management.base import BaseCommand

from ambient_toolbox.import_linter.services import ImportLinterContractService


class Command(BaseCommand):
    """
    Command to validate the currently set import linter contracts as still up to date.
    """

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
