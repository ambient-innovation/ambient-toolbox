

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

