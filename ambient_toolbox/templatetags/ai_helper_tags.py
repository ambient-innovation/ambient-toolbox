from django import template
from django.utils import timezone

register = template.Library()


@register.simple_tag
def js_versiontag():
    return "?s=%s" % timezone.now().microsecond
