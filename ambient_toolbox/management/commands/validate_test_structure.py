from django.core.management.base import BaseCommand

from ambient_toolbox.tests.structure_validator.test_structure_validator import StructureTestValidator


class Command(BaseCommand):
    def handle(self, *args, **options):
        service = StructureTestValidator()
        service.process()
