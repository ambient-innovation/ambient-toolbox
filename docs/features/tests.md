# Tests

## Mixins

### ClassBasedViewTestMixin

This test case mixin helps out when unit-testing a view. It provides methods for the three main ways to request a
view: `get`, `post` and `delete`. Authentication and the creation of the request is handled internally.

````python
class MyViewTestCase(ClassBasedViewTestMixin, TestCase):
    view_class = views.MyView

    def test_get_call_authenticated(self):
        response = self.get(user=self.user, url_params={'pk': 17})
        self.assertEqual(response.status_code, 200)

    def test_get_call_not_authenticated(self):
        response = self.get(user=None, url_params={'pk': 17})
        self.assertEqual(response.status_code, 403)

    def test_post_call(self):
        response = self.post(user=self.user, data={'foo': 'bar'}, url_params={'pk': 17})
        self.assertEqual(response.status_code, 200)

    def test_delete_call(self):
        response = self.delete(user=self.user, url_params={'pk': 17})
        self.assertEqual(response.status_code, 202)
````

### RequestProviderMixin

In many cases, you will find yourself in the position that you need a request in your unittests.
A wise programmer will try to avoid looping the request object through all services — but from time to time you end up
with a well-written method which takes the request as a parameter.

For these cases, the toolbox provides a handy mixin, from which you can derive your test class.
Then you will be able to use a method called `get_request(user=None)`.
If you specify a user, he/she will be the request user.
In most cases you won't need to set an explicit url, so `/` will be taken as a default.
If you do need it, pass set the `url` parameter.

````python
from django.test import TestCase
from ambient_toolbox.tests.mixins import RequestProviderMixin


class MyAwesomeTest(RequestProviderMixin, TestCase):

    def test_something_with_a_request_without_a_user(self):
        request = self.get_request(None)
        ...

    def test_something_with_a_request_having_a_user(self):
        ...
        request = self.get_request(user=my_user)
        ...

    def test_something_with_a_request_with_set_url(self):
        ...
        request = self.get_request(url='/path/to/something')
        ...

````

### BaseViewPermissionTestMixin

Please refer to the view layer section to get details about how to use this view test mixin.

### DjangoMessagingFrameworkTestMixin

If you're working with Django views, you might want to use (and therefore test) the Django messaging framework. To make
this as easy as possible, inherit your view test class from the `DjangoMessagingFrameworkTestMixin`.

You can either check for a full message or just for a partial one.

````python
from django.test import TestCase
from ambient_toolbox.tests.mixins import DjangoMessagingFrameworkTestMixin

class MyViewTest(DjangoMessagingFrameworkTestMixin, TestCase):

    def test_my_message_full_case(self):
        # The view creates a message: "It's sunny on Sundays."
        view = function_to_instantiate_your_view()
        self.assert_full_message_in_request(
            view.request, "It's sunny on Sundays.")

    def test_my_message_partial_case(self):
        # The view creates a message: "I have added *n* new records" with "n" being a variable
        view = function_to_instantiate_your_view()
        self.assert_partial_message_in_request(
            view.request, 'I have added')
````

## Test structure validator

### Motivation

When working on a Django project, it can happen very easily that you create unit tests in a way that they won't be
auto-discovered. The mean thing about this is that you can still run those tests - so it's hard to find those issues.

The most common mistakes are forgetting the `__init__.py` in the directory or not prefixing your python files
with `test_`. To tackle this problem, we created a handy management command you can run manually or integrate in your
CI pipeline.

    python manage.py validate_test_structure

Note: If you enforce 100% coverage in your project, this check is redundant, since the coverage will detect any
tests / test files which are not executed.

### Configuration

You can define all of those settings variables in your main Django settings file.

| Variable                                        | Type | Default                 | Explanation                                                         |
|-------------------------------------------------|------|-------------------------|---------------------------------------------------------------------|
| TEST_STRUCTURE_VALIDATOR_FILE_WHITELIST         | list | []                      | Filenames which will be ignored, will always ignore `__init__`      |
| TEST_STRUCTURE_VALIDATOR_BASE_DIR               | Path | settings.BASE_DIR       | Root path to your application (BASE_DIR in a vanilla Django setup)   |
| TEST_STRUCTURE_VALIDATOR_BASE_APP_NAME          | str  | "apps"                  | Directory where all your Django apps live in, can be set to "".     |
| TEST_STRUCTURE_VALIDATOR_APP_LIST               | list | settings.INSTALLED_APPS | List of all your Django apps you want to validate                   |
| TEST_STRUCTURE_VALIDATOR_IGNORED_DIRECTORY_LIST | list | []                      | Directories which will be ignored, will always ignore `__pycache__` |
