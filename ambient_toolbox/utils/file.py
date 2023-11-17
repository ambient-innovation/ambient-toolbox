import hashlib
import zlib


def get_filename_without_ending(file_path: str) -> str:
    """
    Returns the filename without extension
    """

    # if filename has file_path parts
    if "/" in file_path:
        filename = file_path.rsplit("/")[-1]
    else:
        filename = file_path

    return filename.rsplit(".", 1)[0]


def crc(file_path: str) -> str:
    """Calculates the cyclic redundancy checksum (CRC) of the given file.

    See ``open`` for all the exceptions that can be raised.

    :param file_path: the file for which the CRC checksum should be calculated.
    :return: returns the CRC checksum of the file in hexadecimal format (8 characters).
    """
    prev = 0
    with open(file_path, "rb") as f:
        for line in f:
            prev = zlib.crc32(line, prev)
    return "%08X" % (prev & 0xFFFFFFFF)


def md5_checksum(file_path: str) -> str:
    """
    Returns the md5 checksum of the file from the given file_path.

    See ``open`` for all the exceptions that can be raised.

    :param file_path: the file for which the MD5 hashsum should be calculated.
    :return: returns the MD5 of the file in hexadecimal format.
    """
    with open(file_path, "rb") as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()
