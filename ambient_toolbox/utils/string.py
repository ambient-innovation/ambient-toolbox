import datetime
import os
from typing import Optional, Union

from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import floatformat, slugify
from django.utils.encoding import smart_str

from ambient_toolbox.utils import datetime_format


def distinct(not_distinct_list: list) -> list:
    """
    Returns a list with no duplicate elements
    """
    return list(set(not_distinct_list))


def slugify_file_name(file_name: str, length: int = 40) -> str:
    """
    Slugify the given file name
    """
    name, ext = os.path.splitext(file_name)
    name = smart_str(slugify(name).replace("-", "_"))
    ext = smart_str(slugify(ext))
    result = "{}{}{}".format(name[:length], "." if ext else "", ext)
    return result


def smart_truncate(text: Optional[str], max_length: int = 100, suffix: str = "...") -> str:
    """
    Returns a string of at most `max_length` characters, cutting
    only at word-boundaries. If the string was truncated, `suffix`
    will be appended.
    In comparison to Django's default filter `truncatechars` this method does NOT break words and you
    can choose a custom suffix.
    """
    if text is None:
        return ""

    # Return the string itself if length is smaller or equal to the limit
    if len(text) <= max_length:
        return text

    # Cut the string
    value = text[:max_length]

    # Break into words and remove the last
    words = value.split(" ")[:-1]

    # Join the words and return
    return " ".join(words) + suffix


def float_to_string(value: Optional[float], replacement: str = "0,00") -> str:
    """
    Converts a float to a properly, German-formatted string value
    # todo name is misleading, should contain "de"
    # todo thousand separator would be nice
    If the passed object is None, it will return `replacement`.
    """
    return ("%.2f" % value).replace(".", ",") if value is not None else replacement


def date_to_string(value: Optional[datetime.date], replacement: str = "-", str_format: str = "%d.%m.%Y") -> str:
    """
    Converts a given date "value" to a string formatted with `str_format`.
    If the passed "value" is None, it will return `replacement`.
    """
    return value.strftime(str_format) if value is not None else replacement


def datetime_to_string(
    value: Optional[datetime.datetime], replacement: str = "-", str_format: str = "%d.%m.%Y %H:%M"
) -> str:
    """
    Converts a given datetime "value" to a string formatted with `str_format`.
    If the passed "value" is None, it will return `replacement`.
    """
    return datetime_format(value, str_format) if value is not None else replacement


def number_to_string(value: Optional[Union[int, float]], decimal_digits: int = 0, replacement: str = "-") -> str:
    """
    Converts a given int or float number to a string. Decimal places can be configured via `decimal_digits`.
    If the passed "value" is None, it will return `replacement`.
    Attention: Will not localise the return value!
    """
    return intcomma(floatformat(value, decimal_digits)) if value is not None else replacement


def string_or_none_to_string(value: Optional[any], replacement: str = "-") -> str:
    """
    Converts a given "value" to a string.
    If the passed "value" is None, it will return `replacement`.
    """
    return value if value is not None else replacement


def encode_to_xml(text: str) -> str:
    """
    Encodes ampersand, greater and lower characters in a given string to HTML-entities.
    """
    text_str = str(text)
    text_str = text_str.replace("&", "&amp;")
    text_str = text_str.replace("<", "&lt;")
    text_str = text_str.replace(">", "&gt;")

    return text_str
