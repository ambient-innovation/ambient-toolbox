## Named tuple

### Named tuple helper

#### General

Factory function for quickly making a namedtuple suitable for use in a Django model as a choices attribute on a field.
It will preserve order.

Here you'll find a basic example:

````python
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
````

#### Helpers

````python
# get_choices()
>>> MyModel.COLORS.get_choices()
[(0, 'Black'), (1, 'White')]

# get_choices_dict()
>>> MyModel.COLORS.get_choices_dict()
OrderedDict([(1, 'Black'), (2, 'White')])

# get_all()
>>> lambda  x: (print(color) for color in MyModel.COLORS.get_all())
(1, 'black', 'Black')
(2, 'white', 'White')

# get_choices_tuple()
>>> MyModel.COLORS.get_choices_tuple()
((1, 'black', 'Black'), (2, 'white', 'White'))

# get_values()
>>> MyModel.COLORS.get_values()
[1, 2]

# get_value_by_name()
>>> MyModel.COLORS.get_value_by_name('white')
2

# get_desc_by_value()
>>> MyModel.COLORS.get_desc_by_value(1)
Black

# get_name_by_value()
>>> MyModel.COLORS.get_name_by_value(1)
black

# is_valid()
>>> MyModel.COLORS.is_valid(1)
True
````

### Get value from tuple by key

If you have a tuple ``my_tuple`` and you want to get the value for the key `my_key`, you can use the straight-forward
helper function ``get_value_from_tuple_by_key()``:

```python
my_tuple = (
    1,
    "Value One",
    2,
    "Value Two",
)

my_value = get_value_from_tuple_by_key(my_tuple, 1)
# my_value = 'Value One'
```

### Get key from tuple by value

If you have a tuple ``my_tuple`` and you want to get the key for the value `my_key`, you can use the straight-forward
helper function ``get_key_from_tuple_by_value()``:

```python
my_tuple = (
    1,
    "Value One",
    2,
    "Value Two",
)

my_value = get_key_from_tuple_by_value(my_tuple, "Value One")
# my_value = 1
```
