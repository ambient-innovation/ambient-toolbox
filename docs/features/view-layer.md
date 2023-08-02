# View layer

## Introduction

If you are using django in a fullstack way, meaning with django views and templates, you surely want to use this extra
requirement.

Just install the package like this:

``pip install ambient-toolbox[view-layer]``

If you are using ``pipenv``, you can add the following line to your `Pipfile`:

``ambient-toolbox = {extras = ["view-layer"],version = "*"}``

## Forms

### CrispyLayoutFormMixin

This neat mixin provides a basic setup to turn a regular Django form into a nice bootstrapy crispy form.

````
class MyForm(CrispyLayoutFormMixin, forms.Form):
    pass
````

The form will have the following properties:

| Attribute     | Default configuration                           |
|---------------|-------------------------------------------------|
| Form tag      | Yes                                             |
| Form class    | form-horizontal form-bordered form-row-stripped |
| Method        | POST                                            |
| Submit button | Set, called "Save"                              |
| Label class   | col-md-3                                        |
| Field class   | col-md-9                                        |
| Label size    | col-md-offset-3                                 |

## Formsets

### CountChildrenFormsetMixin

This mixin provides a method which returns the current number of children of this formset. It automatically takes care
of deleted or to-be-deleted children. Have a look at the example use-case below:

````python
class DataFieldFormset(CountChildrenFormsetMixin, BaseInlineFormSet):

    def clean(self):
        cleaned_data = super().clean()

        # Count children
        number_of_children = self.get_number_of_children()

        # do some magic

        return cleaned_data
````

Note that the form needs to be validated before you can use this method.

## Formset Views

This package provides two mixins supporting class-based views combined with formsets. The `FormsetCreateViewMixin` is to
be used with a `generic.CreateView`, the `FormsetUpdateViewMixin` together with `generic.UpdateView`.

The idea behind these mixins to make handling formset less pain and provide the comfy feeling you are used from regular
forms.

Here is an example for a create view:

````python
class MyModelCreateView(FormsetCreateViewMixin, generic.CreateView):
    model = MyModel
    template_name = 'my_app/my_model_edit.html'
    form_class = MyModelEditForm
    formset_class = inlineformset_factory(MyModel, MyModelChild,
                                          form=MyModelChildForm,
                                          formset=MyModelChildFormset)

    def get_formset_kwargs(self):
        # this is optional!
        kwargs = super().get_formset_kwargs()
        kwargs['request'] = self.request
        return kwargs
````

You just define - similar to the regular form - a `formset_class` as a class attribute. All the required handling like
validation will happen magically. If you need to pass additional values to your formset, just extend the method
`get_formset_kwargs()` as you would for djangos `get_form_kwargs()`.

If you want to update a model and its children, here is an example for the edit-case:

````python
class MyModelEditView(FormsetUpdateViewMixin, generic.UpdateView):
    model = MyModel
    template_name = 'my_app/my_model_edit.html'
    form_class = MyModelEditForm
    formset_class = inlineformset_factory(MyModel, MyModelChild,
                                          form=MyModelChildForm,
                                          formset=MyModelChildFormset)

    def get_formset_kwargs(self):
        # this is optional!
        kwargs = super().get_formset_kwargs()
        kwargs['request'] = self.request
        return kwargs
````

## View mixins

### CustomPermissionMixin

If you want to handle some custom permission check for which you cannot use the regular django permissions, just derive
your class-based view from `CustomPermissionMixin` and add the method `validate_permissions()`
with your custom logic. Notice that it has to return a boolean value.

For example, you want to allow only the "owner" of an object to view its detail page:

````python
from django.views import generic


class MyModelDetailView(CustomPermissionMixin, generic.DetailView):
    ...

    def validate_permissions(self):
        object = super().get_object()
        if self.request.user.employee:
            return False
        return True
````

If the method returns `False`, the regular dispatch will just simply render your `403` page and skip all the other
things within the view.

### HtmxResponseMixin

The `HtmxResponseMixin` is a neat helper for passing headers to your HTMX frontend. You can set the
`HX-Redirect` and the `HX-Trigger` headers as a class attribute of your view and don't have to worry about how to fiddle
it into your Django response. Misconfiguration will lead to an error.

#### HX-Redirect

The HTMX docs are very brief about the [HX-Redirect header](https://htmx.org/docs/#response-headers). If you want to
make a call to your backend and in response to this reload your page, you can achieve this as follows:

````python
from ambient_toolbox.view_layer.htmx_mixins import HtmxResponseMixin
from django.urls import reverse_lazy
from django.views import generic


class MyView(HtmxResponseMixin, generic.View):
    hx_redirect_url = reverse_lazy('myapp:mymodel-view')
    ...
````

A typical scenario would be that you delete something from your page or have multiple changes on your previous page you
don't want to update all one by one.

If you need a more elaborate way to set up your redirect url, you can overwrite the getter.

````python
# views.py
from ambient_toolbox.view_layer.htmx_mixins import HtmxResponseMixin
from django.urls import reverse
from django.views import generic


class MyView(HtmxResponseMixin, generic.View):

   def get_hx_redirect_url(self):
      return reverse('myapp:mymodel-view', kwargs={...})
````

#### HX-Trigger

[HX-Triggers](https://htmx.org/docs/#response-headers) will be converted to HTMX javascript events and can be listened
to by your HTMX components in the frontend. Take care that you have to listen on `from:body`, otherwise your events
won't be detected. The moment, your frontend detects the event, a new call to the backend is triggered to rerender the
defined component.

````html
  <a hx-get="{% url 'notification:menu-list' %}"
     hx-trigger="updateNotificationMenu from:body"
     ...>Notifications</a>
````

The `updateNotificationMenu` is the javascript event, which will be sent from the backend.

````python
from ambient_toolbox.view_layer.htmx_mixins import HtmxResponseMixin
from django.views import generic


class MyView(HtmxResponseMixin, generic.View):
    hx_trigger = 'updateNotificationMenu'
    ...
````

This is the most straight-forward case. You send a signal without any context and listen to it with HTMX.

If you want to add context, for example you are using some kind of notification library, like `toastr` or `UIKit`,
you can directly send the along with the event.

````python
# views.py
from ambient_toolbox.view_layer.htmx_mixins import HtmxResponseMixin
from django.views import generic


class MyView(HtmxResponseMixin, generic.View):
    hx_trigger = {'userNotification': 'Stuff happened!'}
    ...
````

This is the required vanilla JS:

````javascript
// base.html or any javascript file
document.body.addEventListener("userNotification", function (e) {
    UIkit.notification({
        message: e.detail.value,
        status: 'success',
        pos: 'top-center',
        timeout: 1000,
    });
});
````

Attention: If you want to send multiple events, you have to use the second option, even if you don't provide any
context.

````python
# views.py
from ambient_toolbox.view_layer.htmx_mixins import HtmxResponseMixin
from django.views import generic


class MyView(HtmxResponseMixin, generic.View):
   hx_trigger = {'updateNotificationMenu': None, 'updateOtherComponent': None}
   ...
````

If you need a more elaborate way to set up your triggers, you can overwrite the getter.

````python
# views.py
from ambient_toolbox.view_layer.htmx_mixins import HtmxResponseMixin
from django.views import generic


class MyView(HtmxResponseMixin, generic.View):

   def get_hx_trigger(self):
      return {'my_event': None}
````



### RequestInFormKwargsMixin

The `RequestInFormKwargsMixin` is a handy helper for passing the request from the view to the form. If you
need for example the current request user within the form, you need to have the current request available.

*Attention: It is encouraged to only pass what you need and therefore - in most cases - pass the user object
using* `UserInFormKwargsMixin` *instead of this mixin.*

Just add the mixin to your class-based view:

````python
from ambient_toolbox.view_layer.views import RequestInFormKwargsMixin
from django.views import generic


# views.py
class MyModelCreateView(RequestInFormKwargsMixin, generic.CreateView):
    model = MyModel
    form_class = MyModelForm
    ...


# forms.py
class MyModelForm(forms.Form):

    def __init__(self, *args, **kwargs):
        # Get request from kwargs
        self.request = kwargs.pop('request')
````

### UserInFormKwargsMixin

The ``UserInFormKwargsMixin`` is a handy helper for passing the request user from the view to the form. A common
use-case would be to set the ownership of the to-be-created object or store the last user changing this record.

Just add the mixin to your class-based view:

````python
from ambient_toolbox.view_layer.views import UserInFormKwargsMixin
from django import forms
from django.views import generic


# views.py
class MyModelCreateView(UserInFormKwargsMixin, generic.CreateView):
    model = MyModel
    form_class = MyModelForm
    ...


# forms.py
class MyModelForm(forms.Form):

    def __init__(self, *args, **kwargs):
        # Get request from kwargs
        self.user = kwargs.pop('user')
````

Make sure that you overwrite the ``__init__`` method of your form and move the `request` to the class. Otherwise
the ``super()`` will detect an unrecognised parameter within the kwargs and raise an error:

````python
from django.forms.models import ModelForm


class MyModelForm(ModelForm):

    def __init__(self, *args, **kwargs):
        # Get request from kwargs
        self.request = kwargs.pop('request', None)

        # Call the parent method
        super().__init__(*args, **kwargs)
````

That's it.

### DjangoPermissionRequiredMixin

#### General setup

In most cases your Django views will require a login and some permissions to access it. Ensuring this manually is
tedious and error-prone. Therefore, we implemented a neat mixin which ensures by default ("security by design" pattern)
that the user needs to be logged in and has the defined permissions.

````python
from ambient_toolbox.view_layer.mixins import DjangoPermissionRequiredMixin
from django.views import generic


class MyModelListView(DjangoPermissionRequiredMixin, generic.ListView):
    model = MyModel
    permission_list = ('account.view_my_model',)
    ...
````

When you extend from this mixin, you can set the class attribute `permission_list` which has to be a list or tuple.

Note, that you have to define the url to your login view, so the mixin can redirect your unauthenticated users
correctly. It defaults to `redirect('login-view')`.

````python
from ambient_toolbox.view_layer.mixins import DjangoPermissionRequiredMixin
from django.views import generic


class MyModelListView(DjangoPermissionRequiredMixin, generic.ListView):
    model = MyModel
    permission_list = ('account.view_my_model',)

    def get_login_url(self):
        return reverse('my-login-view')
````

Alternatively, you can configure your login endpoint, just set the class attribute `login_view_name`. This is the name of your login URL you
have defined in your `urls.py`.

````python
from ambient_toolbox.view_layer.mixins import DjangoPermissionRequiredMixin
from django.views import generic


class MyModelListView(DjangoPermissionRequiredMixin, generic.ListView):
    login_view_name = "account:login-view"
    ...
````

#### Public endpoints

If you require an open view endpoint, just set the class flag `login_required` to False.

````python
from ambient_toolbox.view_layer.mixins import DjangoPermissionRequiredMixin
from django.views import generic


class PublicLandingPageView(DjangoPermissionRequiredMixin, generic.TemplateView):
    login_required = False
    permission_list = ()
    ...
````

#### Testing

##### Setup

As stated above, ensuring that every single view is protected is tedious and error-prone. Therefore, this package
provides a test mixin to ensure the following things:

1. Your view is inheriting from the `DjangoPermissionRequiredMixin` mixin
2. You didn't accidentally break the logic by overwriting important parts, so it ensures that the login barrier and the
   permission test methods are called
3. The permissions are set correctly

The following test case will create a bunch of default test cases covering the points 1-3.

````python
from ambient_toolbox.view_layer.tests.mixins import BaseViewPermissionTestMixin
from django.test import TestCase
from my_project.my_app import views


class MyModelListViewTest(BaseViewPermissionTestMixin, TestCase):
    view_class = views.MyModelListView
    permission_list = ['account.view_my_model']
````

Note, that the permissions are defined redundantly. This approach reduces the risk that you make a copy/paste error when
adding the permissions.

If you have implemented more custom logic, feel free to just add more test cases of your own.

##### Limitations

If you are using the caching decorator directly in a class-based view, the tests will fail. You have to switch to a
class decorator like this:

````python
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views import generic


@method_decorator(cache_page(60 * 10), name='dispatch')
class MyModelListView(generic.ListView):
    ...
````

## Generic views

### ToggleView

Django provides a neat way of enabling the update of a given object through the `generic.UpdateView`. This method will
validate the user data using a given form. But sometimes an update is required which doesn't need any user data being
sent, like toggling a flag or updating a timestamp. For these cases, just use the `ToggleView` - it works basically the
same as the `UpdateView` - except that "POST" is required and that no form has to be defined.

```python
from ambient_toolbox.view_layer.views import ToggleView


class ToggleActiveStateView(ToggleView):
    model = MyModel
    template_name = 'myapp/my_model_edit.html'

    def post(self, request, *args, **kwargs):
        # Update object
        obj = self.get_object()
        obj.is_active = not obj.is_active
        obj.save()

        return render(self.request, self.template_name, {'object': obj})
```
