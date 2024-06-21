# Django REST framework extension

## Serializers

### BaseModelSerializer

This serializers extends the restframework ``ModelSerializer`` but ensures that the ``clean()`` method in the model is
called. By default, only django forms call the model-level clean, not the serializers.

````python
# models.py
class MyModel(models.Model):
    ...

    def clean():
        # here lives the model-level validation
        ...

# serializers.py
class MyModelSerializer(ModelSerializer)
    class Meta:
        model = MyModel

    # do your stuff here!
````

Just derive your serializer from the ``BaseModelSerializer`` and you are good to go!

### CommonInfoSerializer

In addition to the ``CommonInfo`` model class which provides a neat way to set the creator and last editor of any
database object, this serializers takes care of setting those fields if a request user was found.

Furthermore, it extends the ``BaseModelSerializer`` to ensure that model-level validation is called on serializer
validation.

````python
# models.py
class MyOwnershipRelevantModel(CommonInfo):
    ...

# serializers.py
class MyOwnershipRelevantModelSerializer(CommonInfoSerializer)
    class Meta:
        model = MyOwnershipRelevantModel

    # do your stuff here!
````

## Fields

### RecursiveField

In some cases you'll have to define a foreign key from and to the same model. One popular use-case is a simple tree
structure. If you want to use the same serializer for the parent and all children, you can utilise our `RecursiveField`:

````python
class MyModelSerializer(serializers.ModelSerializer):
    ...
    children = RecursiveField(many=True)

    class Meta:
        model = MyModel
        fields = [
            'id',
            ...
            'children',
        ]
````

## Testing of ViewSets

If you want to test `ViewSets` you can use the handy mixin `BaseViewSetTestMixin` from this package. It encapsulates
common use-cases and provides a wrapper to be able to easily focus on your tests and not the syntax of how to call a
viewset manually.

### Setup

It is easy to use this mixin, just follow these steps. You will probably have some base test class to encapsulate your
general test setup. So create a new base api test class like this:

````python
class BaseApiTest(BaseViewSetTestMixin, BaseTest):
    def get_default_api_user(self) -> AbstractUser:
        return baker.make_recipe('apps.account.tests.user')

````

Note that the content of `get_default_api_user()` is just a suggestion. You have to provide the method, but it is
totally up to you how you generate a base request user.

The idea behind this method is, that you define a base user for your API requests. You still have to pass the user
manually to all of your tests in the `execute_request()` method. We did not set this user as a default because the user
is often an essential part of the test and should be selected consciously and with care.

If you do not need this default user, simply return `None` in the described method.

### Test that authentication is required for an endpoint

Permissions are one of the most vital things to test in your application. So this mixin provides a helper method, so you
are able to test what you require without thinking about how to test it.

````python
class MyFancyViewsetApiTest(BaseApiTest):
    def test_list_authentication_required(self):
        self.validate_authentication_required(
            url=reverse('my-fancy-viewset-list'),
            method='get',
            view='list',
        )
````

### Testing CRUD views and custom actions

Here is an example of how to test a CRUD action. The helper method `execute_request()` encapsulates all necessary logic
to create an API response. This response can then be asserted. It is wise to always at first assert the status code. In
this case, if the API does not return valid data, but an error code, the reason of failure is obvious. If you on the
other hand start with asserting response data, you might get an ``IndexError`` which will point the assigned developer
in the wrong direction at first.

````python
class MyFancyViewsetApiTest(BaseApiTest):
    def test_list_regular(self):
        response = self.execute_request(
            method='get',
            url=reverse('my-fancy-viewset-list'),
            viewset_kwargs={'get': 'list'},
            user=self.user,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
````

Notice that you need to tell the viewset which CRUD view you want to test. Here is a list of valid default parameters
you can pass to `viewset_kwargs`:

| Name   | Key    | Value    |
|--------|--------|----------|
| List   | get    | list     |
| Detail | get    | retrieve |
| Create | post   | create   |
| Update | put    | update   |
| Delete | delete | destroy  |

The "Key" is the HTTP method to be used, and the value is the name of the action. If you have a **custom action**, just
choose the corresponding method and pass the action name as "value".

### Validate that a CRUD method is deactivated

It might be vital for your application that some CRUD (create, retrieve, update, delete) views are exposed with a given
viewset but others are not. It happens very easily that a generic DRF mixin is copy-and-pasted and opens an unwanted
`list`, `retrieve`, `create`, etc. endpoint. That is why we recommend testing if all unwanted CRUD methods are
deactivated.

With this mixin you can ensure this easily like this:

````python
class MyFancyViewsetApiTest(BaseApiTest):
    view_class = views.MyFancyViewset
    ...

    def test_create_not_activated(self):
        with self.assertRaises(AttributeError):
            self.execute_request(
                method='post',
                url=reverse('my-fancy-viewset-list'),
                viewset_kwargs={'post': 'create'},
                user=self.user,
            )
````

### Testing file uploads

Here is an example of how to test file uploads. Feel free to adjust the `data` kwarg to suit your needs.

````python
from django.core.files.uploadedfile import SimpleUploadedFile

class MyFancyViewsetApiTest(BaseApiTest):
    view_class = views.MyFancyViewset
    ...

    def test_file_upload_action(self):
        response = self.execute_request(
            method='post',
            url=reverse('my-fancy-viewset-list'),
            viewset_kwargs={'post': 'my-custom-action'},
            user=self.user,
            data={'file': SimpleUploadedFile("file.txt", b"some fancy content")},
            data_format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
````
