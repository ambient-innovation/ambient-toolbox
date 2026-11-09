import contextlib
import sys
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase

from tests.coverage_pragmas.sample_project import SampleProject


class ValidateCoveragePragmasCommandTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = SampleProject()

    @classmethod
    def tearDownClass(cls):
        cls.project.cleanup()
        super().tearDownClass()

    def call_command(self, *args, stdout: StringIO | None = None, **kwargs) -> str:
        stdout = stdout or StringIO()
        with contextlib.chdir(self.project.path):
            call_command("validate_coverage_pragmas", *args, stdout=stdout, **kwargs)
        return stdout.getvalue()

    def test_fails_and_lists_unneeded_pragmas(self):
        stdout = StringIO()
        with self.assertRaisesMessage(CommandError, "Found 3 unneeded coverage pragma(s)."):
            self.call_command(stdout=stdout)

        output = stdout.getvalue()
        self.assertIn("sample.py:2\n", output)
        self.assertIn("omitted.py:1\n", output)
        self.assertIn("sample.py:23  (23)", output)
        self.assertNotIn("Needed pragmas", output)

    def test_lists_needed_pragmas_with_higher_verbosity(self):
        output = self.call_command("never_imported.py", verbosity=2)

        self.assertIn("never_imported.py:1", output)
        self.assertIn("No unneeded coverage pragmas found.", output)

    def test_missing_coverage_data_raises_command_error(self):
        with self.assertRaisesMessage(CommandError, "No coverage data found"):
            self.call_command(data_file="missing")

    def test_missing_extra_raises_command_error(self):
        with (
            mock.patch.dict(sys.modules, {"coverage": None}),
            self.assertRaisesMessage(CommandError, "requires the optional 'coverage-pragmas' extra"),
        ):
            call_command("validate_coverage_pragmas")
