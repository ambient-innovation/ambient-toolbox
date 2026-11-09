import contextlib
from pathlib import Path
from unittest import TestCase

from ambient_toolbox.coverage_pragmas.services import PragmaStatus, UnneededCoveragePragmaService
from tests.coverage_pragmas.sample_project import SampleProject


class UnneededCoveragePragmaServiceTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = SampleProject()
        with contextlib.chdir(cls.project.path):
            cls.findings = {
                (Path(finding.filename).name, finding.line): finding
                for finding in UnneededCoveragePragmaService().get_findings()
            }

    @classmethod
    def tearDownClass(cls):
        cls.project.cleanup()
        super().tearDownClass()

    def assert_finding(self, filename: str, line: int, status: PragmaStatus, missing_lines: list[int] | None = None):
        finding = self.findings[(filename, line)]
        self.assertEqual(finding.status, status)
        self.assertEqual(finding.missing_lines, missing_lines or [])

    def test_executed_function_is_unneeded(self):
        self.assert_finding("sample.py", 2, PragmaStatus.UNNEEDED)

    def test_never_called_function_is_needed(self):
        self.assert_finding("sample.py", 6, PragmaStatus.NEEDED, [7])

    def test_partly_executed_function_is_partial(self):
        self.assert_finding("sample.py", 10, PragmaStatus.PARTIAL, [13])

    def test_unexecuted_single_line_is_needed(self):
        self.assert_finding("sample.py", 18, PragmaStatus.NEEDED, [18])

    def test_executed_condition_with_untaken_branch_is_branch_missing(self):
        self.assert_finding("sample.py", 23, PragmaStatus.BRANCH_MISSING, [23])

    def test_unexecuted_else_is_needed(self):
        self.assert_finding("sample.py", 31, PragmaStatus.NEEDED, [32])

    def test_unused_class_is_needed_despite_definition_lines_running_on_import(self):
        self.assert_finding("sample.py", 35, PragmaStatus.NEEDED, [37])

    def test_pragma_without_effect_is_unneeded(self):
        self.assert_finding("sample.py", 41, PragmaStatus.UNNEEDED)

    def test_pragma_inside_string_is_ignored(self):
        self.assertNotIn(("sample.py", 40), self.findings)

    def test_pragma_in_omitted_file_is_ineffective(self):
        self.assert_finding("omitted.py", 1, PragmaStatus.INEFFECTIVE)

    def test_pragma_in_never_imported_file_is_not_measured(self):
        self.assert_finding("never_imported.py", 1, PragmaStatus.NOT_MEASURED)

    def test_file_that_cannot_be_tokenized_is_skipped(self):
        self.assertNotIn(("broken.py", 1), self.findings)

    def test_paths_limit_the_searched_files(self):
        with contextlib.chdir(self.project.path):
            findings = UnneededCoveragePragmaService(paths=["never_imported.py"]).get_findings()
        filenames = {Path(finding.filename).name for finding in findings}

        self.assertIn("never_imported.py", filenames)
        self.assertNotIn("omitted.py", filenames)

    def test_missing_coverage_data_raises_error(self):
        with contextlib.chdir(self.project.path), self.assertRaisesRegex(ValueError, "No coverage data found"):
            UnneededCoveragePragmaService(data_file="missing").get_findings()


class UnneededCoveragePragmaServiceWithoutBranchDataTest(TestCase):
    def test_executed_condition_is_unneeded_without_branch_data(self):
        project = SampleProject(branch=False)
        self.addCleanup(project.cleanup)

        with contextlib.chdir(project.path):
            findings = UnneededCoveragePragmaService(paths=["sample.py"]).get_findings()

        finding = next(finding for finding in findings if finding.line == 23)  # noqa: PLR2004
        self.assertEqual(finding.status, PragmaStatus.UNNEEDED)
