import os

from django import template
from django.conf import settings

register = template.Library()


@register.filter
def filename(value, max_length=25):
    """
    Shortens the filename to maxlength 25 without loosing the file extension

    :param value:
    :param max_length:
    :return filename with a max length of 25
    """
    name = os.path.basename(value.url)
    if len(name) > max_length:
        ext = name.split(".")[-1]
        name = f"{name[:max_length]}[..].{ext}"
    return name


@register.filter
def filesize(value):
    """
    Returns the filesize of the filename given in value

    :param value:
    :return filesize:
    """
    try:
        return os.path.getsize(f"{settings.MEDIA_ROOT}{value}")
    except Exception:
        return 0
