import tempfile
from pathlib import Path
from unittest import mock

from django.core.management import call_command
from django.test import SimpleTestCase, override_settings

from ambient_toolbox.management.commands.create_translation_file import Command


class CreateTranslationFileCommandTest(SimpleTestCase):
    @mock.patch("ambient_toolbox.management.commands.create_translation_file.call_command")
    @mock.patch("ambient_toolbox.management.commands.create_translation_file.isfile", return_value=True)
    def test_command_with_lang_parameter(self, mock_isfile, mock_call_command):
        mock_content = 'msgid ""\nmsgstr ""\n"POT-Creation-Date: 2024-01-01\\n"\nmsgid "Hello"\nmsgstr ""'

        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(LOCALE_PATHS=[Path(temp_dir)]):
                with mock.patch("builtins.open", mock.mock_open(read_data=mock_content)) as mock_open_file:
                    call_command("create_translation_file", "--lang", "en")

                    mock_call_command.assert_called_once_with("makemessages", "-l", "en", "--no-location", "--no-wrap")
                    # Verify file was opened for reading and writing
                    self.assertEqual(mock_open_file.call_count, 2)

    @mock.patch("ambient_toolbox.management.commands.create_translation_file.call_command")
    @mock.patch("ambient_toolbox.management.commands.create_translation_file.isfile", return_value=True)
    def test_command_strips_quotes_from_lang(self, mock_isfile, mock_call_command):
        mock_content = 'msgid ""\nmsgstr ""\n"POT-Creation-Date: 2024-01-01\\n"\nmsgid "Hello"\nmsgstr ""'

        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(LOCALE_PATHS=[Path(temp_dir)]):
                with mock.patch("builtins.open", mock.mock_open(read_data=mock_content)):
                    call_command("create_translation_file", "--lang", '"en"')

                    mock_call_command.assert_called_once_with("makemessages", "-l", "en", "--no-location", "--no-wrap")

    @mock.patch("ambient_toolbox.management.commands.create_translation_file.call_command")
    @mock.patch("ambient_toolbox.management.commands.create_translation_file.isfile", return_value=True)
    def test_removes_pot_creation_date_lines(self, mock_isfile, mock_call_command):
        mock_content = [
            'msgid ""\n',
            'msgstr ""\n',
            '"POT-Creation-Date: 2024-01-01\\n"\n',
            '"Last-Translator: Test\\n"\n',
            'msgid "Hello"\n',
            'msgstr ""\n',
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(LOCALE_PATHS=[Path(temp_dir)]):
                mock_open = mock.mock_open()
                mock_open.return_value.readlines.return_value = mock_content

                with mock.patch("builtins.open", mock_open):
                    call_command("create_translation_file", "--lang", "en")

                    # Check that writelines was called without POT-Creation-Date line
                    expected_content = [
                        'msgid ""\n',
                        'msgstr ""\n',
                        '"Last-Translator: Test\\n"\n',
                        'msgid "Hello"\n',
                        'msgstr ""\n',
                    ]
                    mock_open.return_value.writelines.assert_called_once_with(expected_content)

    @mock.patch("ambient_toolbox.management.commands.create_translation_file.call_command")
    @mock.patch("ambient_toolbox.management.commands.create_translation_file.isfile", return_value=False)
    def test_raises_error_when_po_file_not_found(self, mock_isfile, mock_call_command):
        with tempfile.TemporaryDirectory() as temp_dir:
            with override_settings(LOCALE_PATHS=[Path(temp_dir)]):
                with self.assertRaises(RuntimeError) as cm:
                    call_command("create_translation_file", "--lang", "en")

                # Check that the error message contains the expected parts
                error_message = str(cm.exception)
                self.assertIn("PO file not found at", error_message)
                self.assertIn("en/LC_MESSAGES/django.po", error_message)

    def test_detect_single_translation_language_with_one_directory(self):
        command = Command()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a language directory
            lang_dir = Path(temp_dir) / "en"
            lang_dir.mkdir()

            with override_settings(LOCALE_PATHS=[Path(temp_dir)]):
                result = command.detect_single_translation_language()
                self.assertEqual(result, "en")

    def test_detect_single_translation_language_with_multiple_directories(self):
        command = Command()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple language directories
            (Path(temp_dir) / "en").mkdir()
            (Path(temp_dir) / "de").mkdir()

            with override_settings(LOCALE_PATHS=[Path(temp_dir)]):
                result = command.detect_single_translation_language()
                self.assertIsNone(result)

    def test_detect_single_translation_language_with_no_directories(self):
        command = Command()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Empty directory
            with override_settings(LOCALE_PATHS=[Path(temp_dir)]):
                result = command.detect_single_translation_language()
                self.assertIsNone(result)

    def test_detect_single_translation_language_with_string_path(self):
        command = Command()

        with tempfile.TemporaryDirectory() as temp_dir:
            # String path instead of Path object
            with override_settings(LOCALE_PATHS=[temp_dir]):
                result = command.detect_single_translation_language()
                self.assertIsNone(result)

    @mock.patch("ambient_toolbox.management.commands.create_translation_file.call_command")
    @mock.patch("ambient_toolbox.management.commands.create_translation_file.isfile", return_value=True)
    def test_command_without_lang_parameter_single_language(self, mock_isfile, mock_call_command):
        mock_content = 'msgid ""\nmsgstr ""'

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create single language directory
            (Path(temp_dir) / "en").mkdir()

            with override_settings(LOCALE_PATHS=[Path(temp_dir)]):
                with mock.patch("builtins.open", mock.mock_open(read_data=mock_content)):
                    call_command("create_translation_file")

                    mock_call_command.assert_called_once_with("makemessages", "-l", "en", "--no-location", "--no-wrap")

    def test_command_without_lang_parameter_no_single_language(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple language directories to avoid single language detection
            (Path(temp_dir) / "en").mkdir()
            (Path(temp_dir) / "de").mkdir()

            with override_settings(LOCALE_PATHS=[Path(temp_dir)]):
                with self.assertRaisesMessage(RuntimeError, 'Please provide a language with the "--lang" parameter.'):
                    call_command("create_translation_file")
