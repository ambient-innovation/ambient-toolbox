from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name="get_first_char")
def get_first_char(value):
    """
    Returns the first char of the given string
    :param value:
    :return:
    """
    return value[:1]


@register.filter(name="concat")
def concat(obj, value: str) -> str:
    """
    Concatenates the two given strings
    """
    return f"{obj}{value}"


@register.filter
@stringfilter
def trim(value):
    """
    Strips the whitespaces of the given value

    :param value:
    :return:
    """
    return value.strip()
