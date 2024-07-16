from typing import Optional

from django.db.models import ForeignKey, Model


def object_to_dict(obj, blacklisted_fields: Optional[list] = None, include_id: bool = False) -> dict:
    """
    Returns a dict with all data defined in the model class as a key-value-dict
    Attention: Does not work for M2M fields!
    """
    # Default blacklist
    blacklisted_fields = blacklisted_fields if blacklisted_fields else []

    # Add default django primary key to blacklist
    if not include_id:
        blacklisted_fields.append("id")

    data = vars(obj)
    valid_data = {}

    valid_fields = []
    for f in obj.__class__._meta.get_fields():
        if type(f) != ForeignKey:
            valid_fields.append(f.name)
        else:
            valid_fields.append(f"{f.name}_id")

    for key, value in list(data.items()):
        if key in valid_fields and key not in blacklisted_fields:
            valid_data[key] = value

    return valid_data


def get_cached_related_obj(obj: Model, related_field_name: str, silently_return_none: bool = False):
    """
    This function helps to avoid silent sub-queries, due to missing `select_related()` or `prefetch_related()`.

    This function performs a lookup in the fields_cache of the given object.
    If silently_return_none is True, this function will return None if the field is not cached.
    Otherwise, an AttributeError will be raised.

    What problem does this function solve?

    foo = Foo.objects.all().get()
    foo.bar  # <-- this will silently cause a sub-query

    foo = Foo.objects.all().select_related('bar').first()
    foo.bar # <-- this will cause no sub-query

    The only difference is the usage of `select_related()`, which can easily be forgotten.

    Usage:
    get_cached_related_obj(foo, 'bar')

    This will result in a KeyError instead of a silent sub-query if the field is not cached
    via `select_related()` or `prefetch_related()`.
    """
    # warning: this is an undocumented feature of django
    fields_cache = obj._state.fields_cache

    if related_field_name in fields_cache:
        return fields_cache[related_field_name]

    if silently_return_none:
        return None

    raise AttributeError(
        f'Field "{related_field_name}" not found in `fields_cache` of {obj.__class__.__name__} object. '
        "Did you forget to use `select_related()` or `prefetch_related()`?"
    )
