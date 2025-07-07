import sys

from django.core.management.base import BaseCommand

from ambient_toolbox.import_linter.services import ImportLinterContractService


class Command(BaseCommand):
    """
    Command to validate the currently set import linter contracts as still up to date.
    """

    def handle(self, *args, **options):
        service = ImportLinterContractService()
        sys.exit(service.validate_contracts())
