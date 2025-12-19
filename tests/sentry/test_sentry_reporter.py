import sys
from unittest import mock

from django.test import TestCase

from ambient_toolbox.sentry.reporter import DjangoQ2SentryReporter


def dummy_task_func():
    pass


class DjangoQ2SentryReporterTest(TestCase):
    @mock.patch("ambient_toolbox.sentry.reporter.sentry_sdk")
    @mock.patch("ambient_toolbox.sentry.reporter.sys")
    def test_report(self, mock_sys, mock_sentry_sdk):
        # Setup
        mock_scope = mock.Mock()
        mock_sentry_sdk.new_scope.return_value.__enter__.return_value = mock_scope

        def error():
            raise ValueError("Test Error")

        # Mock sys.exc_info()
        try:
            error()
        except ValueError:
            exc_info = sys.exc_info()

        mock_sys.exc_info.return_value = exc_info

        reporter = DjangoQ2SentryReporter()

        task_data = {"id": "test_task_id", "name": "test_task_name", "func": dummy_task_func}

        with mock.patch.object(DjangoQ2SentryReporter, "return_task_from_stack", return_value=task_data):
            reporter.report()

        # Verify fingerprint
        self.assertTrue(isinstance(mock_scope.fingerprint, list), "Fingerprint should be a list")
        self.assertEqual(len(mock_scope.fingerprint), 3)
        self.assertEqual(mock_scope.fingerprint[0], "django-q")
        self.assertIn(dummy_task_func.__qualname__, mock_scope.fingerprint[1])
        self.assertIn("Test Error", mock_scope.fingerprint[2])

        # Verify fingerprint elements are strings
        for item in mock_scope.fingerprint:
            self.assertTrue(isinstance(item, str), f"Fingerprint item '{item}' should be a string")

        # Verify extras
        mock_scope.set_extra.assert_any_call("django_q_task_id", "test_task_id")
        mock_scope.set_extra.assert_any_call("django_q_task_name", "test_task_name")
        mock_scope.set_extra.assert_any_call(
            "django_q_task_func", f"{dummy_task_func.__module__}.{dummy_task_func.__qualname__}"
        )

        # Verify capture_exception: expect the exception instance (exc_info[1])
        mock_sentry_sdk.capture_exception.assert_called_once_with(error=exc_info[1])

    @mock.patch("ambient_toolbox.sentry.reporter.sentry_sdk")
    def test_init_sentry_initialized(self, mock_sentry_sdk):
        mock_sentry_sdk.is_initialized.return_value = True
        DjangoQ2SentryReporter()
        mock_sentry_sdk.init.assert_not_called()

    @mock.patch("ambient_toolbox.sentry.reporter.sentry_sdk")
    def test_init_sentry_not_initialized_no_dsn(self, mock_sentry_sdk):
        mock_sentry_sdk.is_initialized.return_value = False
        with self.assertRaises(Exception) as cm:
            DjangoQ2SentryReporter()
        self.assertIn("dsn is required", str(cm.exception))

    @mock.patch("ambient_toolbox.sentry.reporter.sentry_sdk")
    def test_init_sentry_not_initialized_with_dsn(self, mock_sentry_sdk):
        mock_sentry_sdk.is_initialized.return_value = False
        dsn = "https://public@sentry.example.com/1"
        DjangoQ2SentryReporter(dsn=dsn, environment="test")
        mock_sentry_sdk.init.assert_called_once_with(dsn, environment="test")

    @mock.patch("ambient_toolbox.sentry.reporter.traceback", create=True)
    def test_return_task_from_stack_found(self, mock_traceback):
        # Mock traceback object
        mock_tb = mock.Mock()
        mock_tb.tb_next = None  # It is the leaf

        mock_frame = mock.Mock()
        mock_tb.tb_frame = mock_frame
        mock_frame.f_back = None

        expected_task = {"id": "123", "func": dummy_task_func}
        mock_frame.f_locals = {"task": expected_task}

        result = DjangoQ2SentryReporter.return_task_from_stack(mock_tb)
        self.assertEqual(result, expected_task)

    @mock.patch("ambient_toolbox.sentry.reporter.traceback", create=True)
    def test_return_task_from_stack_not_found(self, mock_traceback):
        mock_tb = mock.Mock()
        mock_tb.tb_next = None
        mock_tb.tb_frame.f_back = None
        mock_tb.tb_frame.f_locals = {}

        result = DjangoQ2SentryReporter.return_task_from_stack(mock_tb)
        self.assertEqual(result, {})

    @mock.patch("ambient_toolbox.sentry.reporter.sys")
    @mock.patch("ambient_toolbox.sentry.reporter.traceback", create=True)
    def test_return_task_from_stack_no_tb_arg(self, mock_traceback, mock_sys):
        # Test line 30: if not tb: tb = sys.exc_info()[2]
        mock_tb = mock.Mock()
        mock_tb.tb_next = None
        mock_tb.tb_frame.f_back = None
        mock_tb.tb_frame.f_locals = {}

        mock_sys.exc_info.return_value = (None, None, mock_tb)

        result = DjangoQ2SentryReporter.return_task_from_stack(None)
        self.assertEqual(result, {})
        mock_sys.exc_info.assert_called_once()

    @mock.patch("ambient_toolbox.sentry.reporter.traceback", create=True)
    def test_return_task_from_stack_nested_tb(self, mock_traceback):
        # Test line 34: tb = tb.tb_next
        mock_tb_root = mock.Mock()
        mock_tb_leaf = mock.Mock()

        mock_tb_root.tb_next = mock_tb_leaf
        mock_tb_leaf.tb_next = None

        mock_tb_leaf.tb_frame.f_back = None
        mock_tb_leaf.tb_frame.f_locals = {}

        result = DjangoQ2SentryReporter.return_task_from_stack(mock_tb_root)
        self.assertEqual(result, {})

    @mock.patch("ambient_toolbox.sentry.reporter.traceback", create=True)
    def test_return_task_from_stack_malformed_task(self, mock_traceback):
        # Test line 44: if value.get("id", False) and value.get("func"): -> False
        mock_tb = mock.Mock()
        mock_tb.tb_next = None

        mock_frame = mock.Mock()
        mock_tb.tb_frame = mock_frame
        mock_frame.f_back = None

        # Case 1: task missing func
        mock_frame.f_locals = {"task": {"id": "123"}}
        result = DjangoQ2SentryReporter.return_task_from_stack(mock_tb)
        self.assertEqual(result, {})

        # Case 2: task missing id
        mock_frame.f_locals = {"task": {"func": dummy_task_func}}
        result = DjangoQ2SentryReporter.return_task_from_stack(mock_tb)
        self.assertEqual(result, {})

    @mock.patch("ambient_toolbox.sentry.reporter.traceback", create=True)
    def test_return_task_from_stack_malformed_task_continuation(self, mock_traceback):
        # Test that loop continues if task is malformed
        mock_tb = mock.Mock()
        mock_tb.tb_next = None

        # Frame 1: Malformed task (missing id)
        frame1 = mock.Mock()
        frame1.f_locals = {"task": {"func": dummy_task_func}}

        # Frame 2: Valid task
        frame2 = mock.Mock()
        expected_task = {"id": "123", "func": dummy_task_func}
        frame2.f_locals = {"task": expected_task}

        # Link frames: frame2 is leaf, frame1 is caller (f_back of frame2 is frame1)
        frame2.f_back = frame1
        frame1.f_back = None

        mock_tb.tb_frame = frame2

        result = DjangoQ2SentryReporter.return_task_from_stack(mock_tb)
        self.assertEqual(result, expected_task)

    @mock.patch("ambient_toolbox.sentry.reporter.traceback", create=True)
    def test_return_task_from_stack_task_not_dict(self, mock_traceback):
        # Test that loop continues if task is not a dict
        mock_tb = mock.Mock()
        mock_tb.tb_next = None

        frame1 = mock.Mock()
        frame1.f_locals = {"task": "not a dict"}

        frame2 = mock.Mock()
        expected_task = {"id": "123", "func": dummy_task_func}
        frame2.f_locals = {"task": expected_task}

        frame2.f_back = frame1
        frame1.f_back = None

        mock_tb.tb_frame = frame2

        result = DjangoQ2SentryReporter.return_task_from_stack(mock_tb)
        self.assertEqual(result, expected_task)

    @mock.patch("ambient_toolbox.sentry.reporter.sentry_sdk")
    @mock.patch("ambient_toolbox.sentry.reporter.sys")
    def test_report_func_string(self, mock_sys, mock_sentry_sdk):
        # Verify branch where task["func"] is a string
        mock_scope = mock.Mock()
        mock_sentry_sdk.new_scope.return_value.__enter__.return_value = mock_scope

        def _raise_string_func_error():
            raise ValueError("String Func Error")

        try:
            _raise_string_func_error()
        except ValueError:
            exc_info = sys.exc_info()

        mock_sys.exc_info.return_value = exc_info

        reporter = DjangoQ2SentryReporter()

        task_data = {"id": "task_id", "name": "task_name", "func": "my.module.func"}

        with mock.patch.object(DjangoQ2SentryReporter, "return_task_from_stack", return_value=task_data):
            reporter.report()

        # fingerprint should include the string func path
        self.assertIn("my.module.func", mock_scope.fingerprint[1])
        mock_scope.set_extra.assert_any_call("django_q_task_func", "my.module.func")
        mock_sentry_sdk.capture_exception.assert_called_once_with(error=exc_info[1])

    @mock.patch("ambient_toolbox.sentry.reporter.sentry_sdk")
    @mock.patch("ambient_toolbox.sentry.reporter.sys")
    def test_report_func_unknown(self, mock_sys, mock_sentry_sdk):
        # Verify branch where task["func"] is missing / not callable / not string => "unknown"
        mock_scope = mock.Mock()
        mock_sentry_sdk.new_scope.return_value.__enter__.return_value = mock_scope

        def _raise_unknown_func_error():
            raise ValueError("Unknown Func Error")

        try:
            _raise_unknown_func_error()
        except ValueError:
            exc_info = sys.exc_info()

        mock_sys.exc_info.return_value = exc_info

        reporter = DjangoQ2SentryReporter()

        task_data = {"id": "task_id", "name": "task_name", "func": None}

        with mock.patch.object(DjangoQ2SentryReporter, "return_task_from_stack", return_value=task_data):
            reporter.report()

        self.assertEqual(mock_scope.fingerprint[1], "unknown")
        mock_scope.set_extra.assert_any_call("django_q_task_func", "unknown")
        mock_sentry_sdk.capture_exception.assert_called_once_with(error=exc_info[1])

    @mock.patch("ambient_toolbox.sentry.reporter.traceback", create=True)
    def test_return_task_from_stack_no_tb_frame(self, mock_traceback):
        # Cover the case where tb.tb_frame is None (f becomes None -> immediate return {})
        mock_tb = mock.Mock()
        mock_tb.tb_next = None
        mock_tb.tb_frame = None

        result = DjangoQ2SentryReporter.return_task_from_stack(mock_tb)
        self.assertEqual(result, {})
