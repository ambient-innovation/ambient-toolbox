from unittest import mock

from django.core.management import call_command
from django.test import SimpleTestCase, override_settings


class ValidateTranslationFileIntegrityCommandTest(SimpleTestCase):
    """Test cases for validate_translation_file_integrity management command."""

    @override_settings(LANGUAGES=[("en", "English"), ("de", "German")])
    @mock.patch(
        "ambient_toolbox.management.commands.validate_translation_file_integrity.os.path.isfile", return_value=False
    )
    @mock.patch("builtins.print")
    def test_skips_language_without_po_file(self, mock_print, mock_isfile):
        """Test that languages without PO files are skipped."""
        call_command("validate_translation_file_integrity")

        # Should print language check and skip message for each language
        mock_print.assert_any_call('Check language "English"...')
        mock_print.assert_any_call("> Skipping language due to missing PO file.")
        mock_print.assert_any_call('Check language "German"...')

    @override_settings(LANGUAGES=[("en", "English")])
    @mock.patch(
        "ambient_toolbox.management.commands.validate_translation_file_integrity.os.path.isfile", return_value=True
    )
    @mock.patch("builtins.print")
    def test_all_checks_pass(self, mock_print, mock_isfile):
        """Test that all validation checks pass when everything is correct."""
        with mock.patch(
            "ambient_toolbox.management.commands.validate_translation_file_integrity.subprocess.call"
        ) as mock_subprocess:
            # Return values: fuzzy (1=OK), left-over (1=OK), makemessages (0), git diff (0=OK), untranslated (0=OK)
            mock_subprocess.side_effect = [1, 1, 0, 0, 0]

            call_command("validate_translation_file_integrity")

            # Should print OK message for each check
            ok_calls = [call for call in mock_print.call_args_list if call[0][0] == "OK."]
            # Should have 5 OK messages (fuzzy, left-over, makemessages, diff, untranslated)
            self.assertEqual(len(ok_calls), 5)

    @override_settings(LANGUAGES=[("en", "English")])
    @mock.patch(
        "ambient_toolbox.management.commands.validate_translation_file_integrity.subprocess.call", return_value=0
    )  # Return 0 means match found (fuzzy translations exist)
    @mock.patch(
        "ambient_toolbox.management.commands.validate_translation_file_integrity.os.path.isfile", return_value=True
    )
    @mock.patch("builtins.print")
    def test_raises_exception_on_fuzzy_translations(self, mock_print, mock_isfile, mock_subprocess):
        """Test that exception is raised when fuzzy translations are found."""
        with self.assertRaises(Exception) as cm:
            call_command("validate_translation_file_integrity")

        self.assertIn("Please remove all fuzzy translations", str(cm.exception))
        self.assertIn("./locale/en/LC_MESSAGES/django.po", str(cm.exception))

    @override_settings(LANGUAGES=[("de", "German")])
    @mock.patch(
        "ambient_toolbox.management.commands.validate_translation_file_integrity.os.path.isfile", return_value=True
    )
    @mock.patch("builtins.print")
    def test_raises_exception_on_commented_out_translations(self, mock_print, mock_isfile):
        """Test that exception is raised when commented-out translations are found."""
        with mock.patch(
            "ambient_toolbox.management.commands.validate_translation_file_integrity.subprocess.call"
        ) as mock_subprocess:
            # First call (fuzzy check) returns 1 (OK), second call (commented-out check) returns 0 (found)
            mock_subprocess.side_effect = [1, 0]

            with self.assertRaises(Exception) as cm:
                call_command("validate_translation_file_integrity")

            self.assertIn("Please remove all commented-out translations", str(cm.exception))
            self.assertIn("./locale/de/LC_MESSAGES/django.po", str(cm.exception))

    @override_settings(LANGUAGES=[("fr", "French")])
    @mock.patch(
        "ambient_toolbox.management.commands.validate_translation_file_integrity.os.path.isfile", return_value=True
    )
    @mock.patch("builtins.print")
    def test_raises_exception_on_translation_file_differences(self, mock_print, mock_isfile):
        """Test that exception is raised when translation files have uncommitted changes."""
        with mock.patch(
            "ambient_toolbox.management.commands.validate_translation_file_integrity.subprocess.call"
        ) as mock_subprocess:
            # First two calls (fuzzy, commented-out) return 1 (OK)
            # Third call (makemessages) returns 0
            # Fourth call (git diff) returns 1 (differences found)
            mock_subprocess.side_effect = [1, 1, 0, 1]

            with self.assertRaises(Exception) as cm:
                call_command("validate_translation_file_integrity")

            self.assertIn("It seems you have forgotten to update your translation files", str(cm.exception))
            self.assertIn("manage.py create_translation_file", str(cm.exception))
            self.assertIn("manage.py compilemessages", str(cm.exception))

    @override_settings(LANGUAGES=[("es", "Spanish")])
    @mock.patch(
        "ambient_toolbox.management.commands.validate_translation_file_integrity.os.path.isfile", return_value=True
    )
    @mock.patch("builtins.print")
    def test_raises_exception_on_untranslated_strings(self, mock_print, mock_isfile):
        """Test that exception is raised when untranslated strings are found."""
        with mock.patch(
            "ambient_toolbox.management.commands.validate_translation_file_integrity.subprocess.call"
        ) as mock_subprocess:
            # First two calls (fuzzy, commented-out) return 1 (OK)
            # Third call (makemessages) returns 0
            # Fourth call (git diff) returns 0 (no differences)
            # Fifth call (untranslated check) returns 1 (untranslated strings found)
            mock_subprocess.side_effect = [1, 1, 0, 0, 1]

            with self.assertRaises(Exception) as cm:
                call_command("validate_translation_file_integrity")

            self.assertIn("You have untranslated strings in your translation files", str(cm.exception))

    @override_settings(LANGUAGES=[("en", "English"), ("de", "German")])
    @mock.patch("ambient_toolbox.management.commands.validate_translation_file_integrity.os.path.isfile")
    @mock.patch("builtins.print")
    def test_processes_multiple_languages(self, mock_print, mock_isfile):
        """Test that command processes multiple languages."""
        with mock.patch(
            "ambient_toolbox.management.commands.validate_translation_file_integrity.subprocess.call"
        ) as mock_subprocess:
            # Make only the first language file exist
            mock_isfile.side_effect = lambda path: path == "./locale/en/LC_MESSAGES/django.po"
            # Return values for all checks to pass for English
            mock_subprocess.side_effect = [1, 1, 0, 0, 0]

            call_command("validate_translation_file_integrity")

            # Should check both languages
            mock_print.assert_any_call('Check language "English"...')
            mock_print.assert_any_call('Check language "German"...')
            mock_print.assert_any_call("> Skipping language due to missing PO file.")

    @override_settings(LANGUAGES=[("it", "Italian")])
    @mock.patch(
        "ambient_toolbox.management.commands.validate_translation_file_integrity.os.path.isfile", return_value=True
    )
    @mock.patch("builtins.print")
    def test_correct_subprocess_commands_called(self, mock_print, mock_isfile):
        """Test that correct subprocess commands are called in the right order."""
        with mock.patch(
            "ambient_toolbox.management.commands.validate_translation_file_integrity.subprocess.call"
        ) as mock_subprocess:
            # Return values for all checks to pass
            mock_subprocess.side_effect = [1, 1, 0, 0, 0]

            call_command("validate_translation_file_integrity")

            # Verify the commands called
            calls = mock_subprocess.call_args_list
            self.assertEqual(len(calls), 5)

            # Check fuzzy translations command
            self.assertIn("#, fuzzy", calls[0][0][0])
            self.assertIn("./locale/it/LC_MESSAGES/django.po", calls[0][0][0])

            # Check commented-out translations command
            self.assertIn("#~", calls[1][0][0])
            self.assertIn("./locale/it/LC_MESSAGES/django.po", calls[1][0][0])

            # Check makemessages command
            self.assertIn("python manage.py create_translation_file --lang it", calls[2][0][0])

            # Check git diff command
            self.assertIn("git diff", calls[3][0][0])
            self.assertIn("--ignore-matching-lines=POT-Creation-Date", calls[3][0][0])
            self.assertIn("locale/", calls[3][0][0])

            # Check untranslated strings command
            self.assertIn("msgattrib --untranslated", calls[4][0][0])
            self.assertIn("./locale/it/LC_MESSAGES/django.po", calls[4][0][0])

    @override_settings(LANGUAGES=[])
    @mock.patch("builtins.print")
    def test_handles_empty_languages_list(self, mock_print):
        """Test that command handles empty LANGUAGES setting gracefully."""
        call_command("validate_translation_file_integrity")

        # Should not print any language check messages
        language_check_calls = [call for call in mock_print.call_args_list if "Check language" in str(call)]
        self.assertEqual(len(language_check_calls), 0)

    @override_settings(LANGUAGES=[("pt-br", "Brazilian Portuguese")])
    @mock.patch(
        "ambient_toolbox.management.commands.validate_translation_file_integrity.os.path.isfile", return_value=True
    )
    @mock.patch("builtins.print")
    def test_handles_language_code_with_hyphen(self, mock_print, mock_isfile):
        """Test that command handles language codes with hyphens."""
        with mock.patch(
            "ambient_toolbox.management.commands.validate_translation_file_integrity.subprocess.call"
        ) as mock_subprocess:
            # Return values for all checks to pass
            mock_subprocess.side_effect = [1, 1, 0, 0, 0]

            call_command("validate_translation_file_integrity")

            # Should process the language
            mock_print.assert_any_call('Check language "Brazilian Portuguese"...')

            # Verify subprocess calls use the correct language code
            calls = mock_subprocess.call_args_list
            # Check that pt-br is used in the file path
            self.assertIn("./locale/pt-br/LC_MESSAGES/django.po", calls[0][0][0])

    @override_settings(LANGUAGES=[("zh-hans", "Simplified Chinese")])
    @mock.patch(
        "ambient_toolbox.management.commands.validate_translation_file_integrity.os.path.isfile", return_value=True
    )
    @mock.patch("builtins.print")
    def test_prints_all_check_messages(self, mock_print, mock_isfile):
        """Test that all check messages are printed."""
        with mock.patch(
            "ambient_toolbox.management.commands.validate_translation_file_integrity.subprocess.call"
        ) as mock_subprocess:
            # Return values for all checks to pass
            mock_subprocess.side_effect = [1, 1, 0, 0, 0]

            call_command("validate_translation_file_integrity")

            # Verify all expected messages are printed
            mock_print.assert_any_call('Check language "Simplified Chinese"...')
            mock_print.assert_any_call("> Check for fuzzy translations")
            mock_print.assert_any_call("> Check for left-over translations")
            mock_print.assert_any_call('> Check if "makemessages" detects new translations')
            mock_print.assert_any_call("> Checking for differences in translation file")
            mock_print.assert_any_call("> Check if all translation strings have been translated")

    @override_settings(LANGUAGES=[("ja", "Japanese")])
    @mock.patch(
        "ambient_toolbox.management.commands.validate_translation_file_integrity.os.path.isfile", return_value=True
    )
    @mock.patch("builtins.print")
    def test_git_diff_with_exit_code_greater_than_zero(self, mock_print, mock_isfile):
        """Test that git diff check fails when exit code > 0."""
        with mock.patch(
            "ambient_toolbox.management.commands.validate_translation_file_integrity.subprocess.call"
        ) as mock_subprocess:
            # First two calls (fuzzy, commented-out) return 1 (OK)
            # Third call (makemessages) returns 0
            # Fourth call (git diff) returns 2 (error or differences)
            mock_subprocess.side_effect = [1, 1, 0, 2]

            with self.assertRaises(Exception) as cm:
                call_command("validate_translation_file_integrity")

            self.assertIn("It seems you have forgotten to update your translation files", str(cm.exception))

    @override_settings(LANGUAGES=[("ko", "Korean")])
    @mock.patch(
        "ambient_toolbox.management.commands.validate_translation_file_integrity.os.path.isfile", return_value=True
    )
    @mock.patch("builtins.print")
    def test_untranslated_strings_check_with_any_positive_exit_code(self, mock_print, mock_isfile):
        """Test that untranslated strings check fails for any positive exit code."""
        with mock.patch(
            "ambient_toolbox.management.commands.validate_translation_file_integrity.subprocess.call"
        ) as mock_subprocess:
            # First four calls pass, last call returns a positive number (has untranslated strings)
            mock_subprocess.side_effect = [1, 1, 0, 0, 5]

            with self.assertRaises(Exception) as cm:
                call_command("validate_translation_file_integrity")

            self.assertIn("You have untranslated strings in your translation files", str(cm.exception))

    @override_settings(LANGUAGES=[("ar", "Arabic")])
    @mock.patch(
        "ambient_toolbox.management.commands.validate_translation_file_integrity.os.path.isfile", return_value=True
    )
    @mock.patch("builtins.print")
    def test_all_subprocess_calls_use_shell_true(self, mock_print, mock_isfile):
        """Test that all subprocess calls use shell=True."""
        with mock.patch(
            "ambient_toolbox.management.commands.validate_translation_file_integrity.subprocess.call"
        ) as mock_subprocess:
            # Return values for all checks to pass
            mock_subprocess.side_effect = [1, 1, 0, 0, 0]

            call_command("validate_translation_file_integrity")

            # Verify all calls use shell=True
            for call in mock_subprocess.call_args_list:
                self.assertEqual(call[1].get("shell"), True)
