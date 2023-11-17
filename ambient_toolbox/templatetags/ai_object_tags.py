from django import template

register = template.Library()


@register.simple_tag
def dict_key_lookup(the_dict, key):
    """
    Checks if the given key exists in given dict

    :param the_dict:
    :param key:
    :return: str
    """
    return the_dict.get(key, "")


@register.filter(name="label")
def label(value):
    return value.field.__class__.__name__
