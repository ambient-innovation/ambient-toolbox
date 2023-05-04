from django import template

register = template.Library()


@register.filter
def format_to_minutes(time):
    """
    Converts the seconds to minutes

    :param time:
    :return minutes:
    """

    return time.seconds // 60
