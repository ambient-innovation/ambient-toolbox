from django.core.management.base import BaseCommand

from ambient_toolbox.gitlab.coverage import CoverageService


class Command(BaseCommand):
    """
    Script to validate if the coverage dropped relatively to the default branch.
    Works only with GitLab.
    """

    def handle(self, *args, **options):
        service = CoverageService()
        return service.process()
