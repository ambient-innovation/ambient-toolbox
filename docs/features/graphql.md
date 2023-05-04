# Graphene extension
// todo Needs to be rewritten

## GraphQL based on django ModelForms

Here is a simple Django model in `my_app/models.py`:

```python
from django.db import models

class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
```

Now we create a `ModelForm` in `my_app/forms.py`:

```
from django import forms
from .models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')
```

 We need to create an `ObjectType` which we derive from our model.
 Lives in `my_apps/schemes/schematypes.py`:

```
from graphene_django import DjangoObjectType
from ..models import User

class UserType(DjangoObjectType):
    class Meta:
        model = User
```

 Here's the mutation in `my_app/schema/mutations.py`.
 It takes a `ModelForm` (or a non-model form) to derive the validation rules from:

 ```
import graphene
from graphene_django_ai.forms.mutations import LoginRequiredDjangoModelFormMutation
from .schematypes import UserType
from ..forms import UserForm


class UserCreateUpdateMutation(LoginRequiredDjangoModelFormMutation):
    space = graphene.Field(UserType)

    class Meta:
        form_class = UserForm


# Register new mutation
class UserMutation(graphene.ObjectType):
    spaces = UserCreateUpdateMutation.Field(description='Create and update users')
 ```

 If you register now your `UserMutation` in your schema you have a working model-based and DRY API
 endpoint. Congratulations!

## DeleteMutation for django-model objects

If you want to delete an object you can easily use the `DeleteMutation` like this:

```python
from graphene_django_ai.schemes.mutations import DeleteMutation
from my_app.models import MyModel

class MyModelDeleteMutation(DeleteMutation):
    class Meta:
        model = MyModel
```

If you are using `django-graphql-jwt` authentication you can ensure only logged in access to your delete endpoint like this:

```python
from graphene_django_ai.schemes.mutations import LoginRequiredDeleteMutation
from my_app.models import MyModel

class MyModelDeleteMutation(LoginRequiredDeleteMutation):
    class Meta:
        model = MyModel
```

If you need to customize the **validation** or the **base queryset** you can override methods like this:

```python
from graphene_django_ai.schemes.mutations import LoginRequiredDeleteMutation
from graphql import GraphQLError
from my_app.models import MyModel

class MyModelDeleteMutation(LoginRequiredDeleteMutation):
    class Meta:
        model = MyModel

    def validate(self, request):
        if not request.user.is_superuser:
            raise GraphQLError("This is only allowed for superusers!")

    def get_queryset(self, request):
        return self.model.objects.filter(created_by=request.user)
```

## JWT secure mutations

If you derive your mutation from `LoginRequiredDjangoModelFormMutation` you don't have to manually take
care about securing the login with the decorators.

```python
from graphene_django_ai.forms.mutations import LoginRequiredDjangoModelFormMutation
class MyMutation(LoginRequiredDjangoModelFormMutation):
    ...
```

## Testing GraphQL calls

If you want to unittest your API calls derive your test case from the class `GraphQLTestCase`.

Usage:

```python
import json

from graphene_django.tests.base_test import GraphQLTestCase
from my_project.config.schema import schema

class MyFancyTestCase(GraphQLTestCase):

    # Here you need to inject your test case's schema
    GRAPHQL_SCHEMA = schema

    def test_some_query(self):
        response = self.query(
            '''
            query {
                myModel {
                    id
                    name
                }
            }
            ''',
            op_name='myModel'
        )
        content = json.loads(response.content)
        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        # Add some more asserts if you like
        ...

    def test_some_mutation(self):
        response = self.query(
            '''
            mutation myMutation($input: MyMutationInput!) {
                myMutation(input: $input) {
                    my-model {
                        id
                        name
                    }
                }
            }
            ''',
            op_name='myMutation',
            input_data={'my_field': 'foo', 'other_field': 'bar'}
        )
        # This validates the status code and if you get errors
        self.assertResponseNoErrors(response)

        # Add some more asserts if you like
        ...

    def test_failing_call(self):

       response = self.query(
           '''
           mutation myMutation($input: MyMutationInput!) {
               myMutation(input: $badInput) {
                   my-model {
                       id
                       name
                   }
               }
           }
           ''',
           op_name='myMutation',
           input_data={'my_field': 'foo', 'other_field': 'bar'}
       )
       # This assert tests if the call raised some errors
       # For example if you want to test if invalid input is handled correctly by your endpoint
       self.assertResponseHasErrors(response)

       # Add some more asserts if you like
       ...

```

## GraphQL with Sentry

In some cases you might want to include Sentry while using a GraphQL API. This will probably lead to issues
while using Graphene. This happens because Sentry sends the errors to Sentry as a string and not as error
objects. Because of that all errors are combined and cannot be analyzed. You can use `SentryGraphQLView` for this case.

> **Note**: You must use the following versions of libraries to use this feature!
> * sentry_sdk >= 0.13.0
> * graphene_django >=2.9.1, <3.0

Usage:

```python
# urls.py
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from ambient_toolbox.graphql.views import SentryGraphQLView
from ambient_toolbox.graphql.utils import ignore_graphene_logger

ignore_graphene_logger()    # <-- add this line at global level

# change this line:
path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
# to this:
path("graphql", csrf_exempt(SentryGraphQLView.as_view(graphiql=True))),
```
