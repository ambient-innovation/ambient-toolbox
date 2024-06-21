# Django Admin

This toolbox provides an abundance of useful helpers for the django admin site. Please note that you need to install
the `view-layer` extension of `ambient-toolbox` to use any form-related helpers:

    pip install ambient-toolbox[view-layer]

## Admin classes

### ReadOnlyAdmin

If you want to make a model in the django Admin 100% read-only, you can derive your admin class from ``ReadOnlyAdmin``.
This will ensure that nobody can modify or delete the records of this class in any way.

Either you can register it like this:

````python
admin.site.register(MyModel, ReadOnlyAdmin)
````

Or like this, if you want to customise it further:

````python
@admin.register(MyModel)
class MyModelAdmin(ReadOnlyAdmin):
    ...
````

### EditableOnlyAdmin

If you want to make a model in the django Admin editable, but not create- or deletable, you can simply derive your admin
class from ``EditableOnlyAdmin``. This will ensure that nobody can modify or delete the records of this class in any
way.

Either you can register it like this:

````python
admin.site.register(MyModel, EditableOnlyAdmin)
````

Or like this, if you want to customise it further:

````python
@admin.register(MyModel)
class MyModelAdmin(EditableOnlyAdmin):
    ...
````

## Inlines

### ReadOnlyTabularInline

If you want to make a model ``MyModel`` 100% read-only, but the model is embedded in its parent, `MyParentModel`, you
can derive from the ``ReadOnlyTabularInline``. This will ensure that all instances of ``MyModel`` will not be editable
in any way.

````python
from django.contrib import admin

class MyModelInline(ReadonlyTabularInline):
    model = MyModel
    ...

@admin.register(MyParentModel)
class MyParentModelAdmin(admin.ModelAdmin):
    inlines = [MyModelInline]
    ...
````

## Mixins

### AdminCreateFormMixin

With this mixin you can easily use two different forms for creating and editing an object. The logic is borrowed from
`django.contrib.auth.admin.UserAdmin`, so it's proven django best practice.

Similar to the user creation where you want to set an email and a password at first and later take care about the other
variables, you can now use this pattern for every admin:

````python
from django.contrib import admin

@admin.register(MyModel)
class MyModelAdmin(AdminCreateFormMixin, admin.ModelAdmin):
    add_form = MyModelAddForm
    form = MyModelEditForm
````

### AdminNoInlinesForCreateMixin

This mixin removes all admin inline panels from a given admin class when being in the "create" case. This especially
comes in handy when your inlines have inner dependencies based on the parent model (of the admin class).

````python
from django.contrib import admin

@admin.register(MyModel)
class MyModelAdmin(AdminNoInlinesForCreateMixin, admin.ModelAdmin):
    inlines = (MyFancyInline, MyOtherFancyInline)
````

### AdminRequestInFormMixin

This mixin injects the current request in the form when creating or changing an object of the registered admin class.
Very useful when some data of the form is user-related.

````python
from django.contrib import admin

@admin.register(MyModel)
class MyModelAdmin(AdminRequestInFormMixin, admin.ModelAdmin):
    ...
````

### FetchParentObjectInlineMixin

This mixin injects the parent object of the given inline panel in the formset. Stating the obvious, the parent object is
the object currently being edited in the parent admin class of the given inline class.

This is helpful, if you want to use the parent object for some kind of filtering or validation.

If you need the parent object for a different use-case, have a look at the example below. Here, the new attribute is
used to determine if it is possible to add any new objects of the parent models class. If you want to fetch the parent
object, just call the handy method `get_parent_object_from_request(request)`:

````python
class MyChildModelInline(FetchParentObjectInlineMixin, admin.TabularInline):
    model = MyChildModel
    ...

    def has_add_permission(self, request, obj):
        # Adding is only allowed if the parent object is applicable (all required fields set)
        parent_object = self.get_parent_object_from_request(request)
        if parent_object:
            return MyParentModel.objects.filter(id=parent_object.id).exists()
        return False
````

### FetchObjectMixin

If you need the current object, you can derive from this mixin and use the method `get_object_from_request(request)`.

````python
from django.contrib import admin

@admin.register(MyModel)
class MyModelAdmin(FetchObjectMixin, admin.ModelAdmin):
    ...

    def my_custom_method(self, request):
        current_obj = self.get_object_from_request(request)
        ...
````

### DeactivatableChangeViewAdminMixin

Sometimes when working with groups and permissions, it can happen that you want to show a certain user only the list
view of a model and do not let him/her go to the detail/change view. To avoid unnecessary troubles, this mixin
encapsulates all the stuff you need to achieve this easily.

There are two ways to handle the locking of the change view.

First you can set the boolean class attribute `enable_change_view` to enable or disable the view permanently.

````python
@admin.register(MyModel)
class MyModelNoDetailPageAdmin(DeactivatableChangeViewAdminMixin, admin.ModelAdmin):
    enable_change_view = False
````

If you need a dynamic way to toggle the detail view, you can overwrite the class method `can_see_change_view()`. The
following example only allows access to the detail page for superusers:

````python
@admin.register(MyModel)
class MyModelSuperuserDetailPageAdmin(DeactivatableChangeViewAdminMixin, admin.ModelAdmin):

    def can_see_change_view(self, request) -> bool:
        """
        Superusers can access the detail view, others don't.
        """
        return request.user.is_superuser
````

This mixin automatically disables all links and furthermore the route to the change view so you don't have to worry
about users trying to guess the route.
