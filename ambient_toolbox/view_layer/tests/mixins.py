from typing import Union
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser, Permission
from django.utils.translation import gettext_lazy as _

from ambient_toolbox.tests.errors import TestSetupConfigurationError
from ambient_toolbox.tests.mixins import RequestProviderMixin
from ambient_toolbox.view_layer.mixins import DjangoPermissionRequiredMixin


class BaseViewPermissionTestMixin(RequestProviderMixin):
    view_class = None
    permission_list = None
    view_kwargs = {}

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = cls.get_test_user()

    @classmethod
    def get_test_user(cls):
        return get_user_model().objects.create(username="test_user", email="test.user@ambient-toolbox.com")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if not self.view_class:
            raise TestSetupConfigurationError(_('BaseViewPermissionTestMixin used without setting a "view_class".'))

    def get_view_instance(
        self, *, user: Union[AbstractBaseUser, AnonymousUser], kwargs: dict = None, method: str = "GET"
    ):
        """
        Creates an instance of the given view class and injects a valid request.
        """
        request = self.get_request(user=user, method=method)
        view = self.view_class()
        view.kwargs = kwargs if kwargs else self.view_kwargs
        view.request = request
        return view

    def test_view_class_inherits_mixin(self):
        self.assertTrue(issubclass(self.view_class, DjangoPermissionRequiredMixin))

    def test_permissions_are_equal(self):
        # Sanity checks
        self.assertIsNotNone(self.permission_list, msg="Missing permission list declaration in test.")
        self.assertIsNotNone(self.view_class.permission_list, msg="Missing permission list declaration in view.")

        # Assert same amount of permissions
        self.assertEqual(len(self.permission_list), len(self.view_class.permission_list))

        # Compare target permissions to real permissions
        for permission in self.permission_list:
            self.assertIn(permission, list(self.view_class.permission_list))

        # Compare real permissions to target permissions
        for permission in self.view_class.permission_list:
            self.assertIn(permission, list(self.permission_list))

    def test_permissions_exist_in_database(self):
        for permission in self.permission_list:
            if "." not in permission:
                raise TestSetupConfigurationError(
                    f'View "{self.view_class}" contains ill-formatted permission ' f'"{permission}".'
                )
            app_label, codename = permission.split(".")
            permission_qs = Permission.objects.filter(content_type__app_label=app_label, codename=codename)

            if not permission_qs.exists():
                raise TestSetupConfigurationError(
                    f'View "{self.view_class}" contains invalid permission ' f'"{permission}".'
                )

    def test_passes_login_barrier_is_called(self):
        with mock.patch.object(self.view_class, "passes_login_barrier", return_value=False) as mock_method:
            view = self.get_view_instance(user=AnonymousUser())
            response = view.dispatch(request=view.request, **view.kwargs)
            # If a user is not logged in, he'll be forwarded to the login view
            self.assertEqual(response.status_code, 302)

        mock_method.assert_called_once()

    def test_has_permissions_is_called(self):
        with mock.patch.object(self.view_class, "has_permissions", return_value=False) as mock_method:
            view = self.get_view_instance(user=self.user)
            response = view.dispatch(request=view.request, **view.kwargs)
            self.assertEqual(response.status_code, 403)

        mock_method.assert_called_once()
