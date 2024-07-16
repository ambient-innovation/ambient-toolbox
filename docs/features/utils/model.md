

## Model

### Convert object to dictionary

The function ``object_to_dict(obj, blacklisted_fields, include_id)`` takes an instance of a django model and
extracts all attributes into a dictionary:

````python
from django.db import models
class MyModel(models.Model):
    value1 = models.IntegerField()
    value2 = models.IntegerField()

    ....

obj = MyModel.objects.create(value_1=19, value_2=9)
result = object_to_dict(obj)
# result = {'value_1': 19, 'value_2': 9}
````

Optionally, fields can be excluded with the parameter ``blacklisted_fields``.
Passing a list of field names as string will prevent them from ending up in the result dictionary.

````python
obj = MyModel.objects.create(value_1=19, value_2=9)
result = object_to_dict(obj, ['value_2'])
# result = {'value_1': 19}
````

By default, the model ID is not part of the result. If you want to change this, pass ``include_id=True`` to the function:

````python
obj = MyModel.objects.create(value_1=19, value_2=9)
result = object_to_dict(obj, include_id=True)
# result = {'id': 1, value_1': 19, 'value_2': 9}
````

### get_cached_related_obj(obj, field_name)

The function ``get_cached_related_obj(obj, field_name)`` is supposed to helps avoiding silent sub-queries,
due to missing `select_related()` or `prefetch_related()`.

What problem does this function solve?

```python
foo = Foo.objects.all().first()
foo.bar  # <-- this will silently cause a sub-query
```

```python
foo = Foo.objects.all().select_related("bar").first()
foo.bar  # <-- this will cause no sub-query
```

The only subtle difference is the usage of `select_related()`, which can easily be forgotten.

Usage:

```python
foo = Foo.objects.all().first()
get_cached_related_obj(foo, "bar")
```

This will result in a KeyError instead of a silent sub-query if the field is not cached
via `select_related()` or `prefetch_related()`.

Parameter `silently_return_none` can be set to `True` to return `None` instead of raising an AttributeError.
