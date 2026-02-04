import json
import subprocess
import unittest
from http import HTTPStatus
from unittest import mock

from ambient_toolbox.gitlab.coverage import CoverageService


@mock.patch.dict("os.environ", {"CI_PIPELINE_ID": "17", "CI_PROJECT_ID": "27"})
class CoverageServiceTest(unittest.TestCase):
    def test_get_disable_coverage_integer_false(self):
        service = CoverageService()
        result = service.get_disable_coverage(disable_env="0")

        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_get_disable_coverage_integer_true(self):
        service = CoverageService()
        result = service.get_disable_coverage(disable_env="1")

        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_get_disable_coverage_string_var_bool_false(self):
        service = CoverageService()
        result = service.get_disable_coverage(disable_env="False")

        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_get_disable_coverage_string_var_bool_true(self):
        service = CoverageService()
        result = service.get_disable_coverage(disable_env="True")

        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_get_disable_coverage_string_var_random(self):
        service = CoverageService()
        result = service.get_disable_coverage(disable_env="Wololo")

        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    @mock.patch("subprocess.run")
    def test_get_latest_target_branch_commit_sha(self, mock_run):
        mock_result = mock.MagicMock()
        mock_result.stdout.decode.return_value = "abc123def456\n"
        mock_run.return_value = mock_result

        service = CoverageService()
        result = service.get_latest_target_branch_commit_sha()

        self.assertEqual(result, "abc123def456")
        mock_run.assert_called_once_with(
            ["git", "merge-base", "--fork-point", f"origin/{service.target_branch}"],
            stdout=subprocess.PIPE,
        )

    @mock.patch("httpx.get")
    def test_get_pipeline_id_by_commit_sha_success(self, mock_get):
        mock_response = mock.MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = json.dumps([{"id": 123}]).encode()
        mock_get.return_value = mock_response

        service = CoverageService()
        result = service.get_pipeline_id_by_commit_sha("abc123")

        self.assertEqual(result, 123)

    @mock.patch("httpx.get")
    def test_get_pipeline_id_by_commit_sha_empty_response(self, mock_get):
        mock_response = mock.MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = json.dumps([]).encode()
        mock_get.return_value = mock_response

        service = CoverageService()
        with mock.patch("builtins.print") as mock_print:
            result = service.get_pipeline_id_by_commit_sha("abc123")

        self.assertIsNone(result)
        mock_print.assert_any_call("\n### ERROR: No pipelines found for SHA1 ###\n")

    @mock.patch("httpx.get")
    def test_get_pipeline_id_by_commit_sha_non_200_status(self, mock_get):
        mock_response = mock.MagicMock()
        mock_response.status_code = HTTPStatus.NOT_FOUND
        mock_get.return_value = mock_response

        service = CoverageService()
        result = service.get_pipeline_id_by_commit_sha("abc123")

        self.assertIsNone(result)

    @mock.patch("httpx.get")
    def test_get_coverage_from_pipeline_jobs_api_error(self, mock_get):
        mock_response = mock.MagicMock()
        mock_response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        mock_get.return_value = mock_response

        service = CoverageService()
        with self.assertRaises(ConnectionError) as cm:
            service.get_coverage_from_pipeline(123, "test-job")

        self.assertIn("Call to jobs api endpoint failed with status code 500", str(cm.exception))

    @mock.patch("httpx.get")
    def test_get_coverage_from_pipeline_pipeline_api_error(self, mock_get):
        jobs_response = mock.MagicMock()
        jobs_response.status_code = HTTPStatus.OK
        jobs_response.content = json.dumps([]).encode()

        pipeline_response = mock.MagicMock()
        pipeline_response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

        mock_get.side_effect = [jobs_response, pipeline_response]

        service = CoverageService()
        with self.assertRaises(ConnectionError) as cm:
            service.get_coverage_from_pipeline(123, "test-job")

        self.assertIn("Call to pipeline api endpoint failed with status code 500", str(cm.exception))

    @mock.patch("httpx.get")
    def test_get_coverage_from_pipeline_empty_job_name(self, mock_get):
        jobs_response = mock.MagicMock()
        jobs_response.status_code = HTTPStatus.OK
        jobs_response.content = json.dumps([]).encode()

        pipeline_response = mock.MagicMock()
        pipeline_response.status_code = HTTPStatus.OK
        pipeline_response.content = json.dumps({"coverage": 85.5, "web_url": "http://example.com"}).encode()

        mock_get.side_effect = [jobs_response, pipeline_response]

        service = CoverageService()
        with mock.patch("builtins.print") as mock_print:
            job_cov, total_cov, log = service.get_coverage_from_pipeline(123, "")

        self.assertEqual(job_cov, 85.5)
        self.assertEqual(total_cov, 85.5)
        self.assertIsNone(log)
        mock_print.assert_any_call(
            "\033[91mATTN: No CI_COVERAGE_JOB_NAME provided, using Total Coverage and skipping Coverage Diff\033[0m"
        )

    @mock.patch("httpx.get")
    def test_get_coverage_from_pipeline_job_not_found(self, mock_get):
        jobs_response = mock.MagicMock()
        jobs_response.status_code = HTTPStatus.OK
        jobs_response.content = json.dumps(
            [{"name": "other-job", "coverage": 90.0, "id": 456, "web_url": "http://example.com/job"}]
        ).encode()

        pipeline_response = mock.MagicMock()
        pipeline_response.status_code = HTTPStatus.OK
        pipeline_response.content = json.dumps({"coverage": 85.5, "web_url": "http://example.com"}).encode()

        mock_get.side_effect = [jobs_response, pipeline_response]

        service = CoverageService()
        with mock.patch("builtins.print") as mock_print:
            job_cov, total_cov, log = service.get_coverage_from_pipeline(123, "missing-job")

        self.assertEqual(job_cov, 85.5)
        self.assertEqual(total_cov, 85.5)
        self.assertIsNone(log)
        mock_print.assert_any_call(
            "\033[91mATTN: Failed to get coverage by job name, using Total Coverage and skipping Coverage Diff\033[0m"
        )

    @mock.patch("httpx.get")
    def test_get_coverage_from_pipeline_job_trace_error(self, mock_get):
        jobs_response = mock.MagicMock()
        jobs_response.status_code = HTTPStatus.OK
        jobs_response.content = json.dumps(
            [{"name": "test-job", "coverage": 90.0, "id": 456, "web_url": "http://example.com/job"}]
        ).encode()

        pipeline_response = mock.MagicMock()
        pipeline_response.status_code = HTTPStatus.OK
        pipeline_response.content = json.dumps({"coverage": 85.5, "web_url": "http://example.com"}).encode()

        job_trace_response = mock.MagicMock()
        job_trace_response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

        mock_get.side_effect = [jobs_response, pipeline_response, job_trace_response]

        service = CoverageService()
        with self.assertRaises(ConnectionError) as cm:
            service.get_coverage_from_pipeline(123, "test-job")

        self.assertIn("Call to job api endpoint failed with status code 500", str(cm.exception))

    @mock.patch("httpx.get")
    def test_get_coverage_from_pipeline_success_with_log(self, mock_get):
        jobs_response = mock.MagicMock()
        jobs_response.status_code = HTTPStatus.OK
        jobs_response.content = json.dumps(
            [{"name": "test-job", "coverage": 90.0, "id": 456, "web_url": "http://example.com/job"}]
        ).encode()

        pipeline_response = mock.MagicMock()
        pipeline_response.status_code = HTTPStatus.OK
        pipeline_response.content = json.dumps({"coverage": 85.5, "web_url": "http://example.com"}).encode()

        job_trace_response = mock.MagicMock()
        job_trace_response.status_code = HTTPStatus.OK
        job_trace_response.content = (
            b"Name    Stmts   Miss Branch BrPart  Cover   Missing\ntest.py    10      "
            b"2      0      0    80%     5-6\n3 files skipped due to complete coverage."
        )

        mock_get.side_effect = [jobs_response, pipeline_response, job_trace_response]

        service = CoverageService()
        with mock.patch("builtins.print"):
            job_cov, total_cov, log = service.get_coverage_from_pipeline(123, "test-job")

        self.assertEqual(job_cov, 90.0)
        self.assertEqual(total_cov, 85.5)
        self.assertIn("Name", log)
        self.assertIn("files skipped due to complete coverage", log)

    def test_color_text_coverage_dropped(self):
        result = CoverageService.color_text(-1, "Test coverage", 85.0, 80.0, -5.0)
        expected = "\033[91m Test coverage dropped from 85.00% to 80.00% (Diff: -5.00%).\033[0m"
        self.assertEqual(result, expected)

    def test_color_text_coverage_unchanged(self):
        result = CoverageService.color_text(0, "Test coverage", 85.0, 85.0, 0.0)
        expected = " Test coverage unchanged from 85.00% to 85.00% (Diff: 0.00%).\033[0m"
        self.assertEqual(result, expected)

    def test_color_text_coverage_climbed(self):
        result = CoverageService.color_text(1, "Test coverage", 80.0, 85.0, 5.0)
        expected = "\033[92m Test coverage climbed from 80.00% to 85.00% (Diff: 5.00%).\033[0m"
        self.assertEqual(result, expected)

    @mock.patch("builtins.print")
    def test_print_diff(self, mock_print):
        target_log = (
            "Name    Stmts   Miss Branch BrPart  Cover   Missing\nold.py     10      2      0      0    80%     5-6"
        )
        current_log = (
            "Name    Stmts   Miss Branch BrPart  Cover   Missing\nnew.py     10      1      0      0    90%     5"
        )

        CoverageService.print_diff(target_log, current_log)

        self.assertTrue(mock_print.called)
        # Check that diff headers are printed
        mock_print.assert_any_call("\n############################## Coverage Diff ##############################")

    @mock.patch("builtins.print")
    def test_print_diff_strips_iso_timestamps(self, mock_print):
        # Logs where each line is prefixed with ISO8601 UTC timestamps (GitLab CI default)
        target_log = (
            "2026-02-04T09:12:06.864043Z Name    Stmts   Miss Branch BrPart  Cover   Missing\n"
            "2026-02-04T09:12:06.864043Z file1.py     10      0      0      0    100%\n"
            "2026-02-04T09:12:06.864043Z files skipped due to complete coverage.\n"
        )
        current_log = (
            "2026-02-05T10:15:07.123456Z Name    Stmts   Miss Branch BrPart  Cover   Missing\n"
            "2026-02-05T10:15:07.123456Z file1.py     10      0      0      0    100%\n"
            "2026-02-05T10:15:07.123456Z files skipped due to complete coverage.\n"
        )

        CoverageService.print_diff(target_log, current_log)

        # Combine all printed outputs into single string
        combined = "".join(str(call.args[0]) for call in mock_print.call_args_list if call.args)
        # Timestamps should be stripped from printed output
        self.assertNotIn("2026-02-04T09:12:06.864043Z", combined)
        self.assertNotIn("2026-02-05T10:15:07.123456Z", combined)

    @mock.patch("builtins.print")
    def test_print_diff_with_non_matching_lines(self, mock_print):
        """Test print_diff with lines that don't match the regex pattern to cover branch 185->177."""
        target_log = (
            "Name    Stmts   Miss Branch BrPart  Cover   Missing\n"
            "old.py     10      2      0      0    80%     5-6\n"
            "Some random text that won't match\n"
            "Another line without pattern match"
        )
        current_log = (
            "Name    Stmts   Miss Branch BrPart  Cover   Missing\n"
            "new.py     10      1      0      0    90%     5\n"
            "Some random text that won't match\n"
            "Different random text"
        )

        CoverageService.print_diff(target_log, current_log)

        self.assertTrue(mock_print.called)
        # Check that diff headers are printed
        mock_print.assert_any_call("\n############################## Coverage Diff ##############################")
        # The non-matching lines should be skipped in the output (not printed)
        # Only matching lines (header, changes, etc.) should be printed

    @mock.patch.dict(
        "os.environ",
        {
            "CI_PIPELINE_ID": "100",
            "CI_PROJECT_ID": "200",
            "CI_API_V4_URL": "https://gitlab.example.com/api/v4",
            "CI_COMMIT_REF_NAME": "feature-branch",
            "GITLAB_CI_COVERAGE_PIPELINE_TOKEN": "test-token",
            "GITLAB_CI_DISABLE_COVERAGE": "1",
        },
    )
    @mock.patch("sys.exit")
    def test_process_coverage_disabled(self, mock_exit):
        # Make sys.exit actually exit to prevent further execution
        mock_exit.side_effect = SystemExit(0)

        service = CoverageService()

        with mock.patch("builtins.print") as mock_print:
            with self.assertRaises(SystemExit):
                service.process()

        mock_print.assert_called_with("Coverage was skipped!")
        mock_exit.assert_called_once_with(0)

    @mock.patch.dict(
        "os.environ",
        {
            "CI_PIPELINE_ID": "100",
            "CI_PROJECT_ID": "200",
            "CI_API_V4_URL": "https://gitlab.example.com/api/v4",
            "CI_COMMIT_REF_NAME": "feature-branch",
            "GITLAB_CI_COVERAGE_PIPELINE_TOKEN": "test-token",
            "GITLAB_CI_DISABLE_COVERAGE": "0",
        },
    )
    @mock.patch("httpx.get")
    @mock.patch("subprocess.run")
    @mock.patch("sys.exit")
    def test_process_with_commit_sha_success(self, mock_exit, mock_subprocess, mock_get):
        # Mock subprocess for git command
        mock_result = mock.MagicMock()
        mock_result.stdout.decode.return_value = "abc123\n"
        mock_subprocess.return_value = mock_result

        # Mock pipeline ID lookup by SHA
        sha_response = mock.MagicMock()
        sha_response.status_code = HTTPStatus.OK
        sha_response.content = json.dumps([{"id": 50}]).encode()

        # Mock jobs and pipeline responses for target
        target_jobs_response = mock.MagicMock()
        target_jobs_response.status_code = HTTPStatus.OK
        target_jobs_response.content = json.dumps([]).encode()

        target_pipeline_response = mock.MagicMock()
        target_pipeline_response.status_code = HTTPStatus.OK
        target_pipeline_response.content = json.dumps(
            {"coverage": 80.0, "web_url": "http://example.com/target"}
        ).encode()

        # Mock jobs and pipeline responses for current
        current_jobs_response = mock.MagicMock()
        current_jobs_response.status_code = HTTPStatus.OK
        current_jobs_response.content = json.dumps([]).encode()

        current_pipeline_response = mock.MagicMock()
        current_pipeline_response.status_code = HTTPStatus.OK
        current_pipeline_response.content = json.dumps(
            {"coverage": 85.0, "web_url": "http://example.com/current"}
        ).encode()

        mock_get.side_effect = [
            sha_response,
            target_jobs_response,
            target_pipeline_response,
            current_jobs_response,
            current_pipeline_response,
        ]

        service = CoverageService()

        with mock.patch("builtins.print"):
            service.process()

        # Should not exit with error since coverage improved
        mock_exit.assert_not_called()

    @mock.patch.dict(
        "os.environ",
        {
            "CI_PIPELINE_ID": "100",
            "CI_PROJECT_ID": "200",
            "CI_API_V4_URL": "https://gitlab.example.com/api/v4",
            "CI_COMMIT_REF_NAME": "feature-branch",
            "GITLAB_CI_COVERAGE_PIPELINE_TOKEN": "test-token",
            "GITLAB_CI_DISABLE_COVERAGE": "0",
        },
    )
    @mock.patch("httpx.get")
    @mock.patch("subprocess.run")
    @mock.patch("sys.exit")
    def test_process_without_commit_sha_fallback(self, mock_exit, mock_subprocess, mock_get):
        # Mock subprocess to return empty (no SHA found)
        mock_result = mock.MagicMock()
        mock_result.stdout.decode.return_value = "\n"
        mock_subprocess.return_value = mock_result

        # Mock fallback pipeline lookup
        fallback_response = mock.MagicMock()
        fallback_response.status_code = HTTPStatus.OK
        fallback_response.content = json.dumps([{"id": 60}]).encode()

        # Mock jobs and pipeline responses for target
        target_jobs_response = mock.MagicMock()
        target_jobs_response.status_code = HTTPStatus.OK
        target_jobs_response.content = json.dumps([]).encode()

        target_pipeline_response = mock.MagicMock()
        target_pipeline_response.status_code = HTTPStatus.OK
        target_pipeline_response.content = json.dumps(
            {"coverage": 85.0, "web_url": "http://example.com/target"}
        ).encode()

        # Mock jobs and pipeline responses for current
        current_jobs_response = mock.MagicMock()
        current_jobs_response.status_code = HTTPStatus.OK
        current_jobs_response.content = json.dumps([]).encode()

        current_pipeline_response = mock.MagicMock()
        current_pipeline_response.status_code = HTTPStatus.OK
        current_pipeline_response.content = json.dumps(
            {"coverage": 80.0, "web_url": "http://example.com/current"}
        ).encode()

        mock_get.side_effect = [
            fallback_response,
            target_jobs_response,
            target_pipeline_response,
            current_jobs_response,
            current_pipeline_response,
        ]

        service = CoverageService()

        with mock.patch("builtins.print"):
            service.process()

        # Should exit with error since coverage dropped
        mock_exit.assert_called_once_with(1)

    @mock.patch.dict(
        "os.environ",
        {
            "CI_PIPELINE_ID": "100",
            "CI_PROJECT_ID": "200",
            "CI_API_V4_URL": "https://gitlab.example.com/api/v4",
            "CI_COMMIT_REF_NAME": "feature-branch",
            "GITLAB_CI_COVERAGE_PIPELINE_TOKEN": "test-token",
            "GITLAB_CI_DISABLE_COVERAGE": "0",
        },
    )
    @mock.patch("httpx.get")
    @mock.patch("subprocess.run")
    def test_process_fallback_api_error(self, mock_subprocess, mock_get):
        # Mock subprocess to return empty (no SHA found)
        mock_result = mock.MagicMock()
        mock_result.stdout.decode.return_value = "\n"
        mock_subprocess.return_value = mock_result

        # Mock fallback pipeline lookup with error
        fallback_response = mock.MagicMock()
        fallback_response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        mock_get.return_value = fallback_response

        service = CoverageService()

        with self.assertRaises(ConnectionError) as cm:
            service.process()

        self.assertIn("Call to global pipeline api endpoint failed with status code 500", str(cm.exception))

    @mock.patch.dict(
        "os.environ",
        {
            "CI_PIPELINE_ID": "100",
            "CI_PROJECT_ID": "200",
            "CI_API_V4_URL": "https://gitlab.example.com/api/v4",
            "CI_COMMIT_REF_NAME": "feature-branch",
            "GITLAB_CI_COVERAGE_PIPELINE_TOKEN": "test-token",
            "GITLAB_CI_DISABLE_COVERAGE": "0",
        },
    )
    @mock.patch("httpx.get")
    @mock.patch("subprocess.run")
    def test_process_fallback_empty_pipelines(self, mock_subprocess, mock_get):
        # Mock subprocess to return empty (no SHA found)
        mock_result = mock.MagicMock()
        mock_result.stdout.decode.return_value = "\n"
        mock_subprocess.return_value = mock_result

        # Mock fallback pipeline lookup with empty result
        fallback_response = mock.MagicMock()
        fallback_response.status_code = HTTPStatus.OK
        fallback_response.content = json.dumps([]).encode()

        # Mock jobs and pipeline responses for target (pipeline ID 0)
        target_jobs_response = mock.MagicMock()
        target_jobs_response.status_code = HTTPStatus.OK
        target_jobs_response.content = json.dumps([]).encode()

        target_pipeline_response = mock.MagicMock()
        target_pipeline_response.status_code = HTTPStatus.OK
        target_pipeline_response.content = json.dumps(
            {"coverage": None, "web_url": "http://example.com/target"}
        ).encode()

        # Mock jobs and pipeline responses for current
        current_jobs_response = mock.MagicMock()
        current_jobs_response.status_code = HTTPStatus.OK
        current_jobs_response.content = json.dumps([]).encode()

        current_pipeline_response = mock.MagicMock()
        current_pipeline_response.status_code = HTTPStatus.OK
        current_pipeline_response.content = json.dumps(
            {"coverage": 80.0, "web_url": "http://example.com/current"}
        ).encode()

        mock_get.side_effect = [
            fallback_response,
            target_jobs_response,
            target_pipeline_response,
            current_jobs_response,
            current_pipeline_response,
        ]

        service = CoverageService()

        with mock.patch("builtins.print"):
            service.process()

        # Should handle pipeline ID 0 gracefully

    @mock.patch.dict(
        "os.environ",
        {
            "CI_PIPELINE_ID": "100",
            "CI_PROJECT_ID": "200",
            "CI_API_V4_URL": "https://gitlab.example.com/api/v4",
            "CI_COMMIT_REF_NAME": "feature-branch",
            "GITLAB_CI_COVERAGE_PIPELINE_TOKEN": "test-token",
            "GITLAB_CI_DISABLE_COVERAGE": "0",
            "CI_COVERAGE_JOB_NAME": "test-job",
        },
    )
    @mock.patch("httpx.get")
    @mock.patch("subprocess.run")
    def test_process_with_job_logs_and_diff(self, mock_subprocess, mock_get):
        # Mock subprocess for git command
        mock_result = mock.MagicMock()
        mock_result.stdout.decode.return_value = "abc123\n"
        mock_subprocess.return_value = mock_result

        # Mock pipeline ID lookup by SHA
        sha_response = mock.MagicMock()
        sha_response.status_code = HTTPStatus.OK
        sha_response.content = json.dumps([{"id": 50}]).encode()

        # Mock target pipeline responses
        target_jobs_response = mock.MagicMock()
        target_jobs_response.status_code = HTTPStatus.OK
        target_jobs_response.content = json.dumps(
            [{"name": "test-job", "coverage": 80.0, "id": 500, "web_url": "http://example.com/target-job"}]
        ).encode()

        target_pipeline_response = mock.MagicMock()
        target_pipeline_response.status_code = HTTPStatus.OK
        target_pipeline_response.content = json.dumps(
            {"coverage": 80.0, "web_url": "http://example.com/target"}
        ).encode()

        target_job_trace_response = mock.MagicMock()
        target_job_trace_response.status_code = HTTPStatus.OK
        target_job_trace_response.content = (
            b"Name    Stmts   Miss Branch BrPart  Cover   Missing\nold.py     "
            b"10      2      0      0    80%     5-6\n3 files skipped due "
            b"to complete coverage."
        )

        # Mock current pipeline responses
        current_jobs_response = mock.MagicMock()
        current_jobs_response.status_code = HTTPStatus.OK
        current_jobs_response.content = json.dumps(
            [{"name": "test-job", "coverage": 85.0, "id": 600, "web_url": "http://example.com/current-job"}]
        ).encode()

        current_pipeline_response = mock.MagicMock()
        current_pipeline_response.status_code = HTTPStatus.OK
        current_pipeline_response.content = json.dumps(
            {"coverage": 85.0, "web_url": "http://example.com/current"}
        ).encode()

        current_job_trace_response = mock.MagicMock()
        current_job_trace_response.status_code = HTTPStatus.OK
        current_job_trace_response.content = (
            b"Name    Stmts   Miss Branch BrPart  Cover   "
            b"Missing\nnew.py     10      1      0      0    90%     "
            b"5\n3 files skipped due to complete coverage."
        )

        mock_get.side_effect = [
            sha_response,
            target_jobs_response,
            target_pipeline_response,
            target_job_trace_response,
            current_jobs_response,
            current_pipeline_response,
            current_job_trace_response,
        ]

        service = CoverageService()

        with mock.patch("builtins.print"):
            with mock.patch.object(service, "print_diff") as mock_print_diff:
                service.process()

        # Should call print_diff since both logs are available
        mock_print_diff.assert_called_once()

    @mock.patch.dict(
        "os.environ",
        {
            "CI_PIPELINE_ID": "100",
            "CI_PROJECT_ID": "200",
            "CI_API_V4_URL": "https://gitlab.example.com/api/v4",
            "CI_COMMIT_REF_NAME": "feature-branch",
            "GITLAB_CI_COVERAGE_PIPELINE_TOKEN": "test-token",
            "GITLAB_CI_DISABLE_COVERAGE": "0",
        },
    )
    @mock.patch("httpx.get")
    @mock.patch("subprocess.run")
    def test_process_missing_job_logs_skips_diff(self, mock_subprocess, mock_get):
        # Mock subprocess for git command
        mock_result = mock.MagicMock()
        mock_result.stdout.decode.return_value = "abc123\n"
        mock_subprocess.return_value = mock_result

        # Mock pipeline ID lookup by SHA
        sha_response = mock.MagicMock()
        sha_response.status_code = HTTPStatus.OK
        sha_response.content = json.dumps([{"id": 50}]).encode()

        # Mock jobs and pipeline responses for target (empty job name)
        target_jobs_response = mock.MagicMock()
        target_jobs_response.status_code = HTTPStatus.OK
        target_jobs_response.content = json.dumps([]).encode()

        target_pipeline_response = mock.MagicMock()
        target_pipeline_response.status_code = HTTPStatus.OK
        target_pipeline_response.content = json.dumps(
            {"coverage": 80.0, "web_url": "http://example.com/target"}
        ).encode()

        # Mock jobs and pipeline responses for current (empty job name)
        current_jobs_response = mock.MagicMock()
        current_jobs_response.status_code = HTTPStatus.OK
        current_jobs_response.content = json.dumps([]).encode()

        current_pipeline_response = mock.MagicMock()
        current_pipeline_response.status_code = HTTPStatus.OK
        current_pipeline_response.content = json.dumps(
            {"coverage": 75.0, "web_url": "http://example.com/current"}
        ).encode()

        mock_get.side_effect = [
            sha_response,
            target_jobs_response,
            target_pipeline_response,
            current_jobs_response,
            current_pipeline_response,
        ]

        service = CoverageService()

        with mock.patch("builtins.print") as mock_print:
            with mock.patch("sys.exit") as mock_exit:
                service.process()

        # Should print coverage log not found message
        mock_print.assert_any_call(
            "\n\n\033[91m***************************************************************************\033[0m"
        )
        mock_print.assert_any_call(
            "        \033[91m**/!\\** Coverage log not found. Skipping diff. **/!\\**\033[0m             "
        )

        # Should exit with error since job coverage dropped
        mock_exit.assert_called_once_with(1)
