import os

from django.core.management.base import BaseCommand, CommandError


def _display_path(filename: str) -> str:
    try:
        return os.path.relpath(filename)
    except ValueError:
        # On Windows, a file on another drive than the working directory has no relative path.
        return filename


class Command(BaseCommand):
    """
    Finds "# pragma: no cover" comments which are not required, based on the data of a finished coverage run.
    """

    help = (
        'Lists "# pragma: no cover" comments which exclude code that was executed anyway. '
        "Run your tests with coverage first. Fails if unneeded pragmas are found."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "paths",
            nargs="*",
            help="Files or directories to search for pragmas (default: current directory).",
        )
        parser.add_argument(
            "--data-file",
            default=None,
            help="Path to the coverage data file (default: taken from the coverage configuration).",
        )

    def handle(self, *args, **options):
        # Imports are deferred so projects without the optional `coverage-pragmas` extra
        # can load the management command list without an ImportError.
        try:
            from coverage.exceptions import CoverageException  # noqa: PLC0415
        except ImportError as e:
            raise CommandError(
                "The 'validate_coverage_pragmas' command requires the optional 'coverage-pragmas' extra. "
                "Install it with: pip install ambient-toolbox[coverage-pragmas]"
            ) from e

        from ambient_toolbox.coverage_pragmas.services import (  # noqa: PLC0415
            PragmaStatus,
            UnneededCoveragePragmaService,
        )

        try:
            service = UnneededCoveragePragmaService(paths=options["paths"] or None, data_file=options["data_file"])
            findings = service.get_findings()
        except (ValueError, CoverageException) as e:
            raise CommandError(str(e)) from e

        sections = (
            (PragmaStatus.UNNEEDED, "Unneeded pragmas - removing them does not change the coverage report:"),
            (PragmaStatus.INEFFECTIVE, "Ineffective pragmas - the file is omitted from coverage, remove them:"),
            (
                PragmaStatus.BRANCH_MISSING,
                "Lines executed, but removing the pragma leaves a partial branch (see lines):",
            ),
            (
                PragmaStatus.PARTIAL,
                "Partially executed - the pragma excludes more than necessary (missing lines):",
            ),
            (PragmaStatus.NOT_MEASURED, "No coverage data - the file was never imported during the tests:"),
            (PragmaStatus.NEEDED, "Needed pragmas:"),
        )
        for status, title in sections:
            if status == PragmaStatus.NEEDED and options["verbosity"] < 2:  # noqa: PLR2004
                continue
            section_findings = [finding for finding in findings if finding.status == status]
            if not section_findings:
                continue
            self.stdout.write(self.style.MIGRATE_HEADING(f"\n{title}"))
            for finding in section_findings:
                details = f"  ({', '.join(map(str, finding.missing_lines))})" if finding.missing_lines else ""
                self.stdout.write(f"  {_display_path(finding.filename)}:{finding.line}{details}")

        if service.skipped_files:
            self.stdout.write(self.style.WARNING("\nSkipped files - they could not be read or parsed:"))
            for filename in service.skipped_files:
                self.stdout.write(f"  {_display_path(filename)}")

        failing = [finding for finding in findings if finding.status in service.FAILING_STATUSES]
        if failing:
            raise CommandError(f"Found {len(failing)} unneeded coverage pragma(s).")
        self.stdout.write(self.style.SUCCESS("\nNo unneeded coverage pragmas found."))
