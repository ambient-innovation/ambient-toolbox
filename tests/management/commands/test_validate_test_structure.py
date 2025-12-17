from unittest import mock

from django.core.management import call_command
from django.test import SimpleTestCase

from ambient_toolbox.tests.structure_validator.test_structure_validator import StructureTestValidator


class ValidateTestStructureCommandTest(SimpleTestCase):
    """Test cases for validate_test_structure management command."""

    @mock.patch.object(StructureTestValidator, "process", return_value=None)
    def test_management_command_calls_structure_validator(self, mocked_process):
        """Test that the command calls StructureTestValidator.process()."""
        call_command("validate_test_structure")

        mocked_process.assert_called_once_with()

    @mock.patch.object(StructureTestValidator, "process", side_effect=SystemExit(1))
    def test_management_command_propagates_system_exit(self, mocked_process):
        """Test that SystemExit from StructureTestValidator.process() is propagated."""
        with self.assertRaises(SystemExit) as cm:
            call_command("validate_test_structure")

        self.assertEqual(cm.exception.code, 1)
        mocked_process.assert_called_once_with()

    @mock.patch.object(StructureTestValidator, "process", side_effect=Exception("Validation error"))
    def test_management_command_propagates_exceptions(self, mocked_process):
        """Test that exceptions from StructureTestValidator.process() are propagated."""
        with self.assertRaises(Exception) as cm:
            call_command("validate_test_structure")

        self.assertEqual(str(cm.exception), "Validation error")
        mocked_process.assert_called_once_with()
