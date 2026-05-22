from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Compares the test-coverage percentage of the current branch against the default branch
    using the GitLab API and fails when coverage has dropped.
    """

    help = "Validates that test coverage has not dropped relative to the default branch (GitLab only)."

    def handle(self, *args, **options):
        # Imports are deferred so projects without the optional `gitlab-coverage` extra
        # can load the management command list without an httpx ImportError.
        try:
            import httpx  # noqa: F401, PLC0415
        except ImportError as e:
            raise CommandError(
                "The 'validate_gitlab_coverage' command requires the optional 'gitlab-coverage' extra. "
                "Install it with: pip install ambient-toolbox[gitlab-coverage]"
            ) from e

        from ambient_toolbox.gitlab.coverage import CoverageService  # noqa: PLC0415

        service = CoverageService()
        return service.process()
