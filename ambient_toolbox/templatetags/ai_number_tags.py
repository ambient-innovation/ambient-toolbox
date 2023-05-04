from django import template

register = template.Library()


@register.filter(name='multiply')
def multiply(value, arg):
    """
    Multiplies the arg and the value

    :param value:
    :param arg:
    :return:
    """
    if value:
        value = "%s" % value
        if type(value) is str and len(value) > 0:
            return float(value.replace(",", ".")) * float(arg)

    return None


@register.filter(name='subtract')
def subtract(value, arg):
    """
    Subtracts the arg from the value

    :param value:
    :param arg:
    :return:
    """
    value = value if value is not None else 0
    arg = value if arg is not None else 0
    return int(value) - int(arg)


@register.filter(name='divide')
def divide(value, arg):
    """
    Divides the value by the arg

    :param value:
    :param arg:
    :return:
    """
    if value:
        return value / arg
    else:
        return None


@register.filter(name='to_int')
def to_int(value):
    """
    Parses a string to int value

    :param value:
    :return:
    """
    return int(value) if value else 0


@register.filter(name="currency")
def currency(value):
    """
    Converts the number to an €-amount
    """
    if value:
        return (("%.2f" % round(value, 2)) + "€").replace(".", ",")
    else:
        return "-"
