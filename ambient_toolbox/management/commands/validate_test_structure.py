from django.core.management.base import BaseCommand

from ambient_toolbox.tests.structure_validator.test_structure_validator import TestStructureValidator


class Command(BaseCommand):
    def handle(self, *args, **options):
        service = TestStructureValidator()
        service.process()
