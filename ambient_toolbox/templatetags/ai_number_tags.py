from django import template

register = template.Library()


@register.filter(name="multiply")
def multiply(value, arg):
    """
    Multiplies the arg and the value
    """
    if value:
        value = f"{value}"
        if isinstance(value, str) and len(value) > 0:
            return float(value.replace(",", ".")) * float(arg)

    return None


@register.filter(name="subtract")
def subtract(value, arg):
    """
    Subtracts the arg from the value
    """
    value = value if value is not None else 0
    arg = arg if arg is not None else 0
    return int(value) - int(arg)


@register.filter(name="divide")
def divide(value, arg):
    """
    Divides the value by the arg
    """
    if value:
        return value / arg
    else:
        return None


@register.filter(name="to_int")
def to_int(value):
    """
    Parses a string to int value
    """
    try:
        return int(value)
    except ValueError:
        return 0


@register.filter(name="currency")
def currency(value):
    """
    Converts the number to an €-amount
    """
    if value:
        return (("%.2f" % round(value, 2)) + "€").replace(".", ",")
    else:
        return "-"
