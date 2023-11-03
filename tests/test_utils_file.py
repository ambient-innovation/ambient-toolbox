import pytest

from ambient_toolbox.utils.file import crc, get_filename_without_ending, md5_checksum


def test_get_filename_without_ending_full_path():
    assert get_filename_without_ending("path/to/my/text-file.txt") == "text-file"


def test_get_filename_without_ending_only_filename():
    assert get_filename_without_ending("text-file.txt") == "text-file"


@pytest.fixture
def gen_test_file(tmp_path):
    def inner(content):
        test_file = tmp_path / "test_file.txt"
        test_file.write_text(content)
        return test_file

    return inner


@pytest.mark.parametrize("test_func", [crc, md5_checksum])
def test_closes_file(mocker, test_func):
    """
    Tests if the CRC and MD5 checksum functions use a context manager to open the file, to guarantee that the opened
    file descriptor is closed.
    """
    open_mock = mocker.patch("ambient_toolbox.utils.file.open")
    open_mock.return_value.__enter__.return_value.read.return_value = None  # to make f.read() return None.
    file_mock = mocker.Mock()
    test_func(file_mock)
    assert open_mock.call_args[0][0] == file_mock
    assert open_mock.return_value.__exit__.call_count == 1


@pytest.mark.parametrize(
    "content, crc_result, md5_result",
    [
        ("The answer to life, the universe, and everything.", "31F49620", "f81ab2f7fb6cacf50f973b0dc8faff44"),
        ("The quick brown fox jumps over the lazy dog", "414FA339", "9e107d9d372bb6826bd81d3542a419d6"),
        ("", "00000000", "d41d8cd98f00b204e9800998ecf8427e"),
    ],
)
def test_crc_and_md5(gen_test_file, content, crc_result, md5_result):
    """Generates the CRC and MD5 of a test file and checks its result"""
    test_file = str(gen_test_file(content))
    result = crc(test_file)
    assert result == crc_result
    result = md5_checksum(test_file)
    assert result == md5_result
