from django.core.management.base import BaseCommand

from ambient_toolbox.import_linter.services import ImportLinterContractService


class Command(BaseCommand):
    """
    Regenerates the import-linter contract file from the current settings configuration,
    ensuring the contracts stay in sync with the project structure.
    """

    help = "Updates import-linter contracts from the settings configuration."

    def handle(self, *args, **options):
        service = ImportLinterContractService()
        service.update_contracts()
