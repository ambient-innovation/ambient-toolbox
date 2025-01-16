# Managers

## Per-Object Permission Levels

### Motivation

A frequent requirement for information system database records are often not publicly visible. There are strict rules
who can view what. The django permission system allows restricting access to a whole model but in a lot of cases the
visibility needs to be determined on object level. Let's say we have this data structure:

```python
# models.py
class Company(models.Model):
    name = models.CharField(max_length=100)


class User(models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company)


class Project(models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company)
```

We have a multi-tenant system which helps to organise projects for different companies. As an employee of company "A" I
am only allowed to see all projects belonging to company "A". If we restrict access with the django permissions to the
project model, this would not suit our purpose.

### Custom manager

To tackle this problem, this library provides an abstract class (actually, there are two of them) to help structure
these access levels in a reproducible, understandable and DRY way.

If you derive your managers from ``AbstractUserSpecificManager``, you will expose three methods: `visible_for()`,
`editable_for()` and `deletable_for()`. Each method needs to be implemented per manager class like this:

```python
# managers.py
class ProjectManager(AbstractUserSpecificManager):

    def visible_for(self, user):
        return self.get_queryset().filter(company=user.company)

    def editable_for(self, user):
        return self.get_queryset().filter(company=user.company)

    def deletable_for(self, user):
        return self.get_queryset().filter(company=user.company)
```

Now just register the custom manager within the model:

```python
# models.py
class Project(models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company)

    objects = ProjectManager()
```

Now you can easily use the given methods in every view, service or serializers as follows:

```python
# views.py
def project_list(request):
    project_list = Project.objects.all().visible_for(request.user)
    return render(request, "project/project_list.html", {"project_list": project_list})
```

Obviously, if you are not listing your projects but want to validate if the user is allowed to create/edit or delete the
given object, you should use the other two methods.

### Best practice

#### Custom manager and custom queryset

In most cases you want to implement a custom manager to put your model-related methods into and register a custom
queryset class to handle the permissions.

```python
# managers.py
class ProjectQuerySet(AbstractUserSpecificQuerySet):

    def visible_for(self, user):
        return self.filter(company=user.company)

    def editable_for(self, user):
        return self.filter(company=user.company)

    def deletable_for(self, user):
        return self.filter(company=user.company)


class ProjectManager(models.Manager):

    def get_queryset(self):
        return ProjectQuerySet(self.model, using=self._db)
```

In the model, you'll register only the manager as usual.

```python
# models.py
class Project(models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company)

    objects = ProjectManager()
```

*Update*: If you want to even further improve your coding patterns, you can use the `AbstractUserSpecificSelectorMixin`,
please refer to the "Query Selectors" page.

#### Directly use custom QuerySet class

Under some circumstances, you could skip the manger and directly use a `QuerySet` class as a manager. Therefore, this
package provides the class `AbstractUserSpecificQuerySet`. Usually these circumstances are "small"
models where you don't have custom manager methods. Note that you'll have to refactor your code when you start
implementing custom manger methods!

At first, use a custom queryset class like this:

```python
# managers.py
class ProjectQuerySet(AbstractUserSpecificQuerySet):

    def visible_for(self, user):
        return self.filter(company=user.company)

    def editable_for(self, user):
        return self.filter(company=user.company)

    def deletable_for(self, user):
        return self.filter(company=user.company)
```

Take care that you need to register it a little different in the model:

```python
# models.py
class Project(models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company)

    objects = ProjectQuerySet.as_manager()
```

Then you'll save the `.all()` and can directly use the exposed methods:

```python
project_list = Project.objects.visible_for(request.user)
```

#### Default manager for global visibility

If you have the case that a certain model does not require any user-level permissions, you can use the
``GloballyVisibleQuerySet``. This manager (or more precisely custom queryset) just returns all records when calling any
of its base methods:

```python
def visible_for(self, user):
    return self.all()
```

It is advisable to use this manager for every class. This way, you can ensure that if some permissions are added to a
model, they are put in the right place (the `visible_for()` method) and not somewhere in the code.

Secondly you do not have to decide every time you need the manger if you need to use `visible_for()` or not - just use
it all the time.

Usually you would use this manager for metadata like categories. As pointed out above, you could use the base manager
class BUT if you have to add some user-level permissions later on, you reduce the risk of bad patterns in your code.

#### Get or none

Often you'll find yourself in the situation that you need to get exactly one object from the database but need to handle
the case, that this object is not there (any more).

Imagine, you pass an object ID to a function. Once this function starts, you need to ensure that this object is
still in the database and hasn't been deleted by some other process in the meantime.

Usually, folks would fall back on adding a `first()` to the query and then check if the queryset is `None`. This will
add an ordering parameter to the underlying SQL, which is not necessary and will cause more work for the database.


```python
class MyManager(GetOrNoneManagerMixin, models.Manager):
    pass
```

Therefore, you can use the `GetOrNoneManagerMixin` mixin in your model manager, which provides you with a neat
method called `get_or_none`, similar to Django's `get_or_create`.

You can add as many parameters as you like, just as you can to with `get_or_create`:

```python
obj = MyModel.objects.get_or_none(pk=42)

obj = MyModel.objects.get_or_none(is_active=True, username="Neo.Anderson")
```
