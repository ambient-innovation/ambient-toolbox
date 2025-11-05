import os
import tempfile
from unittest.mock import Mock

from django.test import TestCase, override_settings

from ambient_toolbox.templatetags.ai_file_tags import filename, filesize


class AiFileTagTest(TestCase):
    def test_filename_short(self):
        """Test filename filter with a short filename"""
        mock_file = Mock()
        mock_file.url = "/media/test.pdf"
        self.assertEqual(filename(mock_file), "test.pdf")

    def test_filename_long_exceeds_default_max_length(self):
        """Test filename filter with a long filename exceeding default max_length"""
        mock_file = Mock()
        mock_file.url = "/media/this_is_a_very_long_filename_that_exceeds_max_length.pdf"
        result = filename(mock_file)
        self.assertEqual(result, "this_is_a_very_long_filen[..].pdf")
        self.assertEqual(len(result.split("[..]")[0]), 25)

    def test_filename_long_with_custom_max_length(self):
        """Test filename filter with custom max_length"""
        mock_file = Mock()
        mock_file.url = "/media/this_is_a_very_long_filename.pdf"
        result = filename(mock_file, max_length=10)
        self.assertEqual(result, "this_is_a_[..].pdf")

    def test_filename_exactly_max_length(self):
        """Test filename that is exactly max_length (no truncation needed)"""
        mock_file = Mock()
        # Create a filename that's exactly 25 characters
        mock_file.url = "/media/exactly25characters.txt"
        result = filename(mock_file)
        # Should not be truncated
        self.assertEqual(result, "exactly25characters.txt")

    def test_filename_with_multiple_dots(self):
        """Test filename with multiple dots gets correct extension"""
        mock_file = Mock()
        mock_file.url = "/media/my.very.long.filename.with.many.dots.extension.pdf"
        result = filename(mock_file, max_length=15)
        # Should preserve the last extension
        self.assertTrue(result.endswith(".pdf"))
        self.assertIn("[..]", result)

    @override_settings(MEDIA_ROOT="/tmp/test_media/")
    def test_filesize_file_not_found(self):
        """Test filesize filter when file doesn't exist (exception case)"""
        result = filesize("/nonexistent/file.pdf")
        self.assertEqual(result, 0)

    @override_settings(MEDIA_ROOT="/tmp/")
    def test_filesize_file_exists(self, tmp_path=None):
        """Test filesize filter with existing file"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, dir="/tmp", prefix="test_") as f:
            f.write("test content")
            temp_filename = os.path.basename(f.name)

        try:
            result = filesize(temp_filename)
            self.assertGreater(result, 0)
        finally:
            # Clean up
            os.unlink(f"/tmp/{temp_filename}")

    def test_filesize_with_path(self):
        """Test filesize with a path string"""
        result = filesize("/some/path/file.txt")
        # Should return 0 when file doesn't exist
        self.assertEqual(result, 0)
