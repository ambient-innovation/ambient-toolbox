import os

from django.core.management.base import BaseCommand, CommandError

SECTIONS = (
    ("unneeded", "Unneeded pragmas - everything they exclude was executed, remove them:"),
    ("ineffective", "Ineffective pragmas - the file is omitted from coverage, remove them:"),
    ("branch_missing", "Lines executed, but removing the pragma leaves a partial branch (see lines):"),
    ("partial", "Partially executed - the pragma excludes more than necessary (missing lines):"),
    ("not_measured", "No coverage data - the file was never imported during the tests:"),
    ("needed", "Needed pragmas:"),
)


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
            help='Path to the coverage data file (default: ".coverage").',
        )

    def handle(self, *args, **options):
        # Imports are deferred so projects without the optional `coverage-pragmas` extra
        # can load the management command list without an ImportError.
        try:
            import coverage  # noqa: F401, PLC0415
        except ImportError as e:
            raise CommandError(
                "The 'validate_coverage_pragmas' command requires the optional 'coverage-pragmas' extra. "
                "Install it with: pip install ambient-toolbox[coverage-pragmas]"
            ) from e

        from ambient_toolbox.coverage_pragmas.services import UnneededCoveragePragmaService  # noqa: PLC0415

        service = UnneededCoveragePragmaService(paths=options["paths"] or None, data_file=options["data_file"])
        try:
            findings = service.get_findings()
        except ValueError as e:
            raise CommandError(str(e)) from e

        for status_value, title in SECTIONS:
            if status_value == "needed" and options["verbosity"] < 2:  # noqa: PLR2004
                continue
            section_findings = [finding for finding in findings if finding.status.value == status_value]
            if not section_findings:
                continue
            self.stdout.write(self.style.MIGRATE_HEADING(f"\n{title}"))
            for finding in section_findings:
                location = f"{os.path.relpath(finding.filename)}:{finding.line}"
                details = f"  ({', '.join(map(str, finding.missing_lines))})" if finding.missing_lines else ""
                self.stdout.write(f"  {location}{details}")

        failing = [finding for finding in findings if finding.status in service.FAILING_STATUSES]
        if failing:
            raise CommandError(f"Found {len(failing)} unneeded coverage pragma(s).")
        self.stdout.write(self.style.SUCCESS("\nNo unneeded coverage pragmas found."))
