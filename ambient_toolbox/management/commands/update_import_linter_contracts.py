from django.core.management.base import BaseCommand

from ambient_toolbox.import_linter.services import ImportLinterContractService


class Command(BaseCommand):
    """
    Command to update the import linter contracts based on the settings configuration.
    """

    def handle(self, *args, **options):
        service = ImportLinterContractService()
        service.update_contracts()
