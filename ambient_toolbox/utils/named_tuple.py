from collections import OrderedDict, namedtuple
from typing import Any


def get_namedtuple_choices(name, choices_tuple):
    """
    Made by Ross Crawford-d'Heureuse.

    Factory function for quickly making a namedtuple suitable for use in a
    Django model as a choices attribute on a field. It will preserve order.

    Usage::

        class MyModel(models.Model):
            COLORS = get_namedtuple_choices('COLORS', (
                (0, 'black', 'Black'),
                (1, 'white', 'White'),
            ))
            colors = models.PositiveIntegerField(choices=COLORS)

        >>> MyModel.COLORS.black
        0
        >>> MyModel.COLORS.get_choices()
        [(0, 'Black'), (1, 'White')]

        class OtherModel(models.Model):
            GRADES = get_namedtuple_choices('GRADES', (
                ('FR', 'fr', 'Freshman'),
                ('SR', 'sr', 'Senior'),
            ))
            grade = models.CharField(max_length=2, choices=GRADES)

        >>> OtherModel.GRADES.fr
        'FR'
        >>> OtherModel.GRADES.get_choices()
        [('fr', 'Freshman'), ('sr', 'Senior')]
    """

    class Choices(namedtuple(name, [name for val, name, desc in choices_tuple])):
        __slots__ = ()
        _choices = tuple(desc for val, name, desc in choices_tuple)

        def get_choices(self):
            return list(zip(tuple(self), self._choices))

        def get_choices_dict(self):
            """
            Return an ordered dict of key and their values
            must be ordered correctly as there are items that depend on the key
            order
            """
            choices = OrderedDict()
            for k, v in self.get_choices():
                choices[k] = v
            return choices

        def get_all(self):
            yield from choices_tuple

        def get_choices_tuple(self):
            return choices_tuple

        def get_values(self):
            values = []
            for val, _name, _desc in choices_tuple:
                if isinstance(val, type([])):
                    values.extend(val)
                else:
                    values.append(val)
            return values

        def get_value_by_name(self, input_name):
            for val, _name, _desc in choices_tuple:
                if _name == input_name:
                    return val
            return False

        def get_desc_by_value(self, input_value):
            for val, _name, _desc in choices_tuple:
                if val == input_value:
                    return _desc
            return False

        def get_name_by_value(self, input_value):
            for val, _name, _desc in choices_tuple:
                if val == input_value:
                    return _name
            return False

        def is_valid(self, selection):
            for val, _name, _desc in choices_tuple:
                if selection in (val, _name, _desc):
                    return True
            return False

    return Choices._make([val for val, name, desc in choices_tuple])


def get_value_from_tuple_by_key(choices: tuple, key) -> Any:
    """
    Fetches the tuple value by a given key
    Useful for getting the name of a key from a model choice tuple of tuples.
    Usage: project_type_a_name = get_value_from_tuple_by_key(PROJECT_TYPE_CHOICES, PROJECT_TYPE_A)
    """
    try:
        return dict(choices)[key]
    except KeyError:
        return "-"


def get_key_from_tuple_by_value(choices: tuple, value) -> Any:
    """
    Fetches the tuple key by a given value
    Useful for getting the key of a value from a model choice tuple of tuples.
    Usage: project_type_a_name = get_value_from_tuple_by_key(PROJECT_TYPE_CHOICES, 'Budget-Project')
    """
    try:
        return [x[0] for x in choices if x[1] == value][0]
    except IndexError:
        return "-"
