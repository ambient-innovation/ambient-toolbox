from unittest import mock

from django.db import OperationalError
from django.test import TestCase, override_settings

from ambient_toolbox.services.custom_scrubber import AbstractScrubbingService, ScrubbingError


class ScrubbingErrorTest(TestCase):
    """Test suite for ScrubbingError exception."""

    def test_scrubbing_error_is_runtime_error(self):
        """Test that ScrubbingError is a subclass of RuntimeError."""
        self.assertTrue(issubclass(ScrubbingError, RuntimeError))

    def test_scrubbing_error_can_be_raised(self):
        """Test that ScrubbingError can be raised with a message."""
        with self.assertRaises(ScrubbingError) as context:
            raise ScrubbingError("Test error message")
        self.assertEqual(str(context.exception), "Test error message")


class AbstractScrubbingServiceTest(TestCase):
    """Test suite for AbstractScrubbingService."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = AbstractScrubbingService()

    def test_init_creates_logger(self):
        """Test that __init__ creates a logger with the correct name."""
        service = AbstractScrubbingService()
        self.assertEqual(service._logger.name, "django_scrubber")

    def test_default_user_password_constant(self):
        """Test that DEFAULT_USER_PASSWORD constant is set correctly."""
        self.assertEqual(self.service.DEFAULT_USER_PASSWORD, "Admin0404!")

    def test_default_keep_session_data(self):
        """Test that keep_session_data is False by default."""
        self.assertFalse(self.service.keep_session_data)

    def test_default_keep_scrubber_data(self):
        """Test that keep_scrubber_data is False by default."""
        self.assertFalse(self.service.keep_scrubber_data)

    def test_default_keep_django_admin_log(self):
        """Test that keep_django_admin_log is False by default."""
        self.assertFalse(self.service.keep_django_admin_log)

    def test_default_pre_scrub_functions(self):
        """Test that pre_scrub_functions is empty list by default."""
        self.assertEqual(self.service.pre_scrub_functions, [])

    def test_default_post_scrub_functions(self):
        """Test that post_scrub_functions is empty list by default."""
        self.assertEqual(self.service.post_scrub_functions, [])

    @mock.patch("ambient_toolbox.services.custom_scrubber.make_password")
    def test_get_hashed_default_password_regular(self, mocked_make_password):
        """Test that _get_hashed_default_password calls make_password correctly."""
        self.service._get_hashed_default_password()
        mocked_make_password.assert_called_once_with(self.service.DEFAULT_USER_PASSWORD)

    @override_settings(DEBUG=False)
    def test_validation_fails_when_debug_mode_inactive(self):
        """Test that _validation returns False when DEBUG is False."""
        self.assertFalse(self.service._validation())

    @override_settings(DEBUG=True, INSTALLED_APPS=[])
    def test_validation_fails_when_scrubber_not_installed(self):
        """Test that _validation returns False when django_scrubber is not installed."""
        self.assertFalse(self.service._validation())

    @override_settings(DEBUG=True, LOGGING={"loggers": {}})
    @mock.patch("ambient_toolbox.services.custom_scrubber.settings")
    def test_validation_warns_when_logging_not_configured(self, mock_settings):
        """Test that _validation warns when django_scrubber logging is not configured but returns True."""
        mock_settings.DEBUG = True
        mock_settings.INSTALLED_APPS = ["django_scrubber"]
        mock_settings.LOGGING = {"loggers": {}}

        with self.assertLogs("django_scrubber", level="WARNING") as log:
            result = self.service._validation()
        self.assertTrue(result)
        self.assertIn("Logging for django-scrubber is not activated", log.output[0])

    @override_settings(DEBUG=True, LOGGING={"loggers": {"django_scrubber": {}}})
    @mock.patch("ambient_toolbox.services.custom_scrubber.settings")
    def test_validation_succeeds_with_all_checks_passing(self, mock_settings):
        """Test that _validation returns True when all checks pass."""
        mock_settings.DEBUG = True
        mock_settings.INSTALLED_APPS = ["django_scrubber"]
        mock_settings.LOGGING = {"loggers": {"django_scrubber": {}}}

        result = self.service._validation()
        self.assertTrue(result)

    @override_settings(DEBUG=False)
    def test_process_raises_error_when_validation_fails(self):
        """Test that process raises ScrubbingError when validation fails."""
        with self.assertRaisesMessage(ScrubbingError, "Scrubber settings validation failed"):
            self.service.process()

    @override_settings(DEBUG=True, LOGGING={"loggers": {"django_scrubber": {}}})
    @mock.patch("ambient_toolbox.services.custom_scrubber.settings")
    @mock.patch("ambient_toolbox.services.custom_scrubber.call_command")
    @mock.patch("ambient_toolbox.services.custom_scrubber.Session")
    @mock.patch("ambient_toolbox.services.custom_scrubber.LogEntry")
    def test_process_calls_scrub_data_command(self, mock_log_entry, mock_session, mock_call_command, mock_settings):
        """Test that process calls the scrub_data command."""
        mock_settings.DEBUG = True
        mock_settings.INSTALLED_APPS = ["django_scrubber"]
        mock_settings.LOGGING = {"loggers": {"django_scrubber": {}}}

        with mock.patch("ambient_toolbox.services.custom_scrubber.connections") as mock_connections:
            mock_cursor = mock.MagicMock()
            mock_connections.__getitem__.return_value.cursor.return_value = mock_cursor

            result = self.service.process()

        self.assertTrue(result)
        mock_call_command.assert_called_once_with("scrub_data")

    @override_settings(DEBUG=True, LOGGING={"loggers": {"django_scrubber": {}}})
    @mock.patch("ambient_toolbox.services.custom_scrubber.settings")
    @mock.patch("ambient_toolbox.services.custom_scrubber.call_command")
    @mock.patch("ambient_toolbox.services.custom_scrubber.Session")
    @mock.patch("ambient_toolbox.services.custom_scrubber.LogEntry")
    def test_process_calls_pre_scrub_functions(self, mock_log_entry, mock_session, mock_call_command, mock_settings):
        """Test that process calls pre_scrub_functions in order."""
        mock_settings.DEBUG = True
        mock_settings.INSTALLED_APPS = ["django_scrubber"]
        mock_settings.LOGGING = {"loggers": {"django_scrubber": {}}}

        service = AbstractScrubbingService()
        service.pre_scrub_functions = ["pre_function_1", "pre_function_2"]
        service.pre_function_1 = mock.MagicMock()
        service.pre_function_2 = mock.MagicMock()

        with mock.patch("ambient_toolbox.services.custom_scrubber.connections") as mock_connections:
            mock_cursor = mock.MagicMock()
            mock_connections.__getitem__.return_value.cursor.return_value = mock_cursor

            result = service.process()

        self.assertTrue(result)
        service.pre_function_1.assert_called_once()
        service.pre_function_2.assert_called_once()

        # Verify order: pre functions called before scrub_data
        call_order = [call.args for call in mock_call_command.mock_calls]
        self.assertEqual(len(call_order), 1)

    @override_settings(DEBUG=True, LOGGING={"loggers": {"django_scrubber": {}}})
    @mock.patch("ambient_toolbox.services.custom_scrubber.settings")
    @mock.patch("ambient_toolbox.services.custom_scrubber.call_command")
    @mock.patch("ambient_toolbox.services.custom_scrubber.Session")
    @mock.patch("ambient_toolbox.services.custom_scrubber.LogEntry")
    def test_process_calls_post_scrub_functions(self, mock_log_entry, mock_session, mock_call_command, mock_settings):
        """Test that process calls post_scrub_functions in order."""
        mock_settings.DEBUG = True
        mock_settings.INSTALLED_APPS = ["django_scrubber"]
        mock_settings.LOGGING = {"loggers": {"django_scrubber": {}}}

        service = AbstractScrubbingService()
        service.post_scrub_functions = ["post_function_1", "post_function_2"]
        service.post_function_1 = mock.MagicMock()
        service.post_function_2 = mock.MagicMock()

        with mock.patch("ambient_toolbox.services.custom_scrubber.connections") as mock_connections:
            mock_cursor = mock.MagicMock()
            mock_connections.__getitem__.return_value.cursor.return_value = mock_cursor

            result = service.process()

        self.assertTrue(result)
        service.post_function_1.assert_called_once()
        service.post_function_2.assert_called_once()

    @override_settings(DEBUG=True, LOGGING={"loggers": {"django_scrubber": {}}})
    @mock.patch("ambient_toolbox.services.custom_scrubber.settings")
    @mock.patch("ambient_toolbox.services.custom_scrubber.call_command")
    @mock.patch("ambient_toolbox.services.custom_scrubber.Session")
    @mock.patch("ambient_toolbox.services.custom_scrubber.LogEntry")
    def test_process_deletes_django_admin_log_when_not_kept(
        self, mock_log_entry, mock_session, mock_call_command, mock_settings
    ):
        """Test that process deletes LogEntry objects when keep_django_admin_log is False."""
        mock_settings.DEBUG = True
        mock_settings.INSTALLED_APPS = ["django_scrubber"]
        mock_settings.LOGGING = {"loggers": {"django_scrubber": {}}}

        service = AbstractScrubbingService()
        service.keep_django_admin_log = False

        with mock.patch("ambient_toolbox.services.custom_scrubber.connections") as mock_connections:
            mock_cursor = mock.MagicMock()
            mock_connections.__getitem__.return_value.cursor.return_value = mock_cursor

            result = service.process()

        self.assertTrue(result)
        mock_log_entry.objects.all().delete.assert_called_once()

    @override_settings(DEBUG=True, LOGGING={"loggers": {"django_scrubber": {}}})
    @mock.patch("ambient_toolbox.services.custom_scrubber.settings")
    @mock.patch("ambient_toolbox.services.custom_scrubber.call_command")
    @mock.patch("ambient_toolbox.services.custom_scrubber.Session")
    @mock.patch("ambient_toolbox.services.custom_scrubber.LogEntry")
    def test_process_keeps_django_admin_log_when_configured(
        self, mock_log_entry, mock_session, mock_call_command, mock_settings
    ):
        """Test that process does not delete LogEntry objects when keep_django_admin_log is True."""
        mock_settings.DEBUG = True
        mock_settings.INSTALLED_APPS = ["django_scrubber"]
        mock_settings.LOGGING = {"loggers": {"django_scrubber": {}}}

        service = AbstractScrubbingService()
        service.keep_django_admin_log = True

        with mock.patch("ambient_toolbox.services.custom_scrubber.connections") as mock_connections:
            mock_cursor = mock.MagicMock()
            mock_connections.__getitem__.return_value.cursor.return_value = mock_cursor

            result = service.process()

        self.assertTrue(result)
        mock_log_entry.objects.all().delete.assert_not_called()

    @override_settings(DEBUG=True, LOGGING={"loggers": {"django_scrubber": {}}})
    @mock.patch("ambient_toolbox.services.custom_scrubber.settings")
    @mock.patch("ambient_toolbox.services.custom_scrubber.call_command")
    @mock.patch("ambient_toolbox.services.custom_scrubber.Session")
    @mock.patch("ambient_toolbox.services.custom_scrubber.LogEntry")
    def test_process_deletes_session_data_when_not_kept(
        self, mock_log_entry, mock_session, mock_call_command, mock_settings
    ):
        """Test that process deletes Session objects when keep_session_data is False."""
        mock_settings.DEBUG = True
        mock_settings.INSTALLED_APPS = ["django_scrubber"]
        mock_settings.LOGGING = {"loggers": {"django_scrubber": {}}}

        service = AbstractScrubbingService()
        service.keep_session_data = False

        with mock.patch("ambient_toolbox.services.custom_scrubber.connections") as mock_connections:
            mock_cursor = mock.MagicMock()
            mock_connections.__getitem__.return_value.cursor.return_value = mock_cursor

            result = service.process()

        self.assertTrue(result)
        mock_session.objects.all().delete.assert_called_once()

    @override_settings(DEBUG=True, LOGGING={"loggers": {"django_scrubber": {}}})
    @mock.patch("ambient_toolbox.services.custom_scrubber.settings")
    @mock.patch("ambient_toolbox.services.custom_scrubber.call_command")
    @mock.patch("ambient_toolbox.services.custom_scrubber.Session")
    @mock.patch("ambient_toolbox.services.custom_scrubber.LogEntry")
    def test_process_keeps_session_data_when_configured(
        self, mock_log_entry, mock_session, mock_call_command, mock_settings
    ):
        """Test that process does not delete Session objects when keep_session_data is True."""
        mock_settings.DEBUG = True
        mock_settings.INSTALLED_APPS = ["django_scrubber"]
        mock_settings.LOGGING = {"loggers": {"django_scrubber": {}}}

        service = AbstractScrubbingService()
        service.keep_session_data = True

        with mock.patch("ambient_toolbox.services.custom_scrubber.connections") as mock_connections:
            mock_cursor = mock.MagicMock()
            mock_connections.__getitem__.return_value.cursor.return_value = mock_cursor

            result = service.process()

        self.assertTrue(result)
        mock_session.objects.all().delete.assert_not_called()

    @override_settings(DEBUG=True, LOGGING={"loggers": {"django_scrubber": {}}})
    @mock.patch("ambient_toolbox.services.custom_scrubber.settings")
    @mock.patch("ambient_toolbox.services.custom_scrubber.call_command")
    @mock.patch("ambient_toolbox.services.custom_scrubber.Session")
    @mock.patch("ambient_toolbox.services.custom_scrubber.LogEntry")
    def test_process_truncates_scrubber_data_when_not_kept(
        self, mock_log_entry, mock_session, mock_call_command, mock_settings
    ):
        """Test that process truncates scrubber data when keep_scrubber_data is False."""
        mock_settings.DEBUG = True
        mock_settings.INSTALLED_APPS = ["django_scrubber"]
        mock_settings.LOGGING = {"loggers": {"django_scrubber": {}}}

        service = AbstractScrubbingService()
        service.keep_scrubber_data = False

        with mock.patch("ambient_toolbox.services.custom_scrubber.connections") as mock_connections:
            mock_cursor = mock.MagicMock()
            mock_connections.__getitem__.return_value.cursor.return_value = mock_cursor

            result = service.process()

        self.assertTrue(result)
        mock_cursor.execute.assert_called_once_with("TRUNCATE TABLE django_scrubber_fakedata;")

    @override_settings(DEBUG=True, LOGGING={"loggers": {"django_scrubber": {}}})
    @mock.patch("ambient_toolbox.services.custom_scrubber.settings")
    @mock.patch("ambient_toolbox.services.custom_scrubber.call_command")
    @mock.patch("ambient_toolbox.services.custom_scrubber.Session")
    @mock.patch("ambient_toolbox.services.custom_scrubber.LogEntry")
    def test_process_deletes_scrubber_data_when_truncate_fails(
        self, mock_log_entry, mock_session, mock_call_command, mock_settings
    ):
        """Test that process falls back to DELETE when TRUNCATE raises OperationalError (e.g., SQLite)."""
        mock_settings.DEBUG = True
        mock_settings.INSTALLED_APPS = ["django_scrubber"]
        mock_settings.LOGGING = {"loggers": {"django_scrubber": {}}}

        service = AbstractScrubbingService()
        service.keep_scrubber_data = False

        with mock.patch("ambient_toolbox.services.custom_scrubber.connections") as mock_connections:
            mock_cursor = mock.MagicMock()
            # First call raises OperationalError, second call succeeds
            mock_cursor.execute.side_effect = [OperationalError("TRUNCATE not supported"), None]
            mock_connections.__getitem__.return_value.cursor.return_value = mock_cursor

            result = service.process()

        self.assertTrue(result)
        # Verify both TRUNCATE and DELETE were attempted
        self.assertEqual(mock_cursor.execute.call_count, 2)
        mock_cursor.execute.assert_any_call("TRUNCATE TABLE django_scrubber_fakedata;")
        mock_cursor.execute.assert_any_call("DELETE FROM django_scrubber_fakedata;")

    @override_settings(DEBUG=True, LOGGING={"loggers": {"django_scrubber": {}}})
    @mock.patch("ambient_toolbox.services.custom_scrubber.settings")
    @mock.patch("ambient_toolbox.services.custom_scrubber.call_command")
    @mock.patch("ambient_toolbox.services.custom_scrubber.Session")
    @mock.patch("ambient_toolbox.services.custom_scrubber.LogEntry")
    def test_process_keeps_scrubber_data_when_configured(
        self, mock_log_entry, mock_session, mock_call_command, mock_settings
    ):
        """Test that process does not truncate scrubber data when keep_scrubber_data is True."""
        mock_settings.DEBUG = True
        mock_settings.INSTALLED_APPS = ["django_scrubber"]
        mock_settings.LOGGING = {"loggers": {"django_scrubber": {}}}

        service = AbstractScrubbingService()
        service.keep_scrubber_data = True

        with mock.patch("ambient_toolbox.services.custom_scrubber.connections") as mock_connections:
            mock_cursor = mock.MagicMock()
            mock_connections.__getitem__.return_value.cursor.return_value = mock_cursor

            result = service.process()

        self.assertTrue(result)
        mock_cursor.execute.assert_not_called()

    @override_settings(DEBUG=True, LOGGING={"loggers": {"django_scrubber": {}}})
    @mock.patch("ambient_toolbox.services.custom_scrubber.settings")
    @mock.patch("ambient_toolbox.services.custom_scrubber.call_command")
    @mock.patch("ambient_toolbox.services.custom_scrubber.Session")
    @mock.patch("ambient_toolbox.services.custom_scrubber.LogEntry")
    def test_process_returns_true_on_success(self, mock_log_entry, mock_session, mock_call_command, mock_settings):
        """Test that process returns True when successful."""
        mock_settings.DEBUG = True
        mock_settings.INSTALLED_APPS = ["django_scrubber"]
        mock_settings.LOGGING = {"loggers": {"django_scrubber": {}}}

        with mock.patch("ambient_toolbox.services.custom_scrubber.connections") as mock_connections:
            mock_cursor = mock.MagicMock()
            mock_connections.__getitem__.return_value.cursor.return_value = mock_cursor

            result = self.service.process()

        self.assertTrue(result)

    @override_settings(DEBUG=True, LOGGING={"loggers": {"django_scrubber": {}}})
    @mock.patch("ambient_toolbox.services.custom_scrubber.settings")
    @mock.patch("ambient_toolbox.services.custom_scrubber.call_command")
    @mock.patch("ambient_toolbox.services.custom_scrubber.Session")
    @mock.patch("ambient_toolbox.services.custom_scrubber.LogEntry")
    def test_process_logs_all_steps(self, mock_log_entry, mock_session, mock_call_command, mock_settings):
        """Test that process logs all important steps during execution."""
        mock_settings.DEBUG = True
        mock_settings.INSTALLED_APPS = ["django_scrubber"]
        mock_settings.LOGGING = {"loggers": {"django_scrubber": {}}}

        service = AbstractScrubbingService()

        with mock.patch("ambient_toolbox.services.custom_scrubber.connections") as mock_connections:
            mock_cursor = mock.MagicMock()
            mock_connections.__getitem__.return_value.cursor.return_value = mock_cursor

            with self.assertLogs("django_scrubber", level="INFO") as log:
                result = service.process()

        self.assertTrue(result)
        log_output = " ".join(log.output)
        self.assertIn("Start scrubbing process", log_output)
        self.assertIn("Validating setup", log_output)
        self.assertIn('Scrubbing data with "scrub_data"', log_output)
        self.assertIn('Clearing data from "django_session"', log_output)
        self.assertIn('Clearing data from "django_scrubber_fakedata"', log_output)
        self.assertIn("Scrubbing finished", log_output)
