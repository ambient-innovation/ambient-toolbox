"""
Tests for BaseViewPermissionTestMixin test helper class.
This module ensures comprehensive coverage of the test utility mixin used for testing
view permissions in Django applications.
"""

from unittest import mock

import pytest
from django.contrib.auth.models import AnonymousUser, Permission, User
from django.http import HttpResponse
from django.test import TestCase
from django.views import generic

from ambient_toolbox.tests.errors import TestSetupConfigurationError
from ambient_toolbox.view_layer.mixins import DjangoPermissionRequiredMixin
from ambient_toolbox.view_layer.tests.mixins import BaseViewPermissionTestMixin


class TestViewWithPermissions(DjangoPermissionRequiredMixin, generic.View):
    """Test view with properly configured permissions."""

    permission_list = ("auth.change_user",)
    login_view_name = "other-login-view"

    def get(self, *args, **kwargs):
        return HttpResponse(status=200)


class TestViewMultiplePermissions(DjangoPermissionRequiredMixin, generic.View):
    """Test view with multiple permissions."""

    permission_list = ("auth.change_user", "auth.add_user")
    login_view_name = "other-login-view"

    def get(self, *args, **kwargs):
        return HttpResponse(status=200)


class TestViewNoPermissionList(DjangoPermissionRequiredMixin, generic.View):
    """Test view without permission_list attribute."""

    login_view_name = "other-login-view"

    def get(self, *args, **kwargs):
        return HttpResponse(status=200)


class ValidBaseViewPermissionTest(BaseViewPermissionTestMixin, TestCase):
    """Test case using BaseViewPermissionTestMixin correctly."""

    view_class = TestViewWithPermissions
    permission_list = ("auth.change_user",)


class ValidMultiplePermissionsTest(BaseViewPermissionTestMixin, TestCase):
    """Test case with multiple permissions."""

    view_class = TestViewMultiplePermissions
    permission_list = ("auth.change_user", "auth.add_user")


class BaseViewPermissionTestMixinInitTest(TestCase):
    """Tests for __init__ method of BaseViewPermissionTestMixin."""

    def test_init_without_view_class_raises_error(self):
        """Test that initializing without view_class raises TestSetupConfigurationError."""

        class TestWithoutViewClass(BaseViewPermissionTestMixin, TestCase):
            view_class = None
            permission_list = ("auth.change_user",)

        with pytest.raises(TestSetupConfigurationError) as exc_info:
            TestWithoutViewClass("test_view_class_inherits_mixin")

        assert 'BaseViewPermissionTestMixin used without setting a "view_class"' in str(exc_info.value)

    def test_init_with_view_class_succeeds(self):
        """Test that initializing with view_class works correctly."""

        class TestWithViewClass(BaseViewPermissionTestMixin, TestCase):
            view_class = TestViewWithPermissions
            permission_list = ("auth.change_user",)

        # Should not raise any error
        test_instance = TestWithViewClass("test_view_class_inherits_mixin")
        assert test_instance.view_class == TestViewWithPermissions


class BaseViewPermissionTestMixinGetTestUserTest(TestCase):
    """Tests for get_test_user class method."""

    def test_get_test_user_creates_user(self):
        """Test that get_test_user creates a user with correct attributes."""
        user = ValidBaseViewPermissionTest.get_test_user()

        assert user.username == "test_user"
        assert user.email == "test.user@ambient-toolbox.com"
        assert User.objects.filter(username="test_user").exists()


class BaseViewPermissionTestMixinSetUpTestDataTest(TestCase):
    """Tests for setUpTestData class method."""

    def test_setup_test_data_creates_user(self):
        """Test that setUpTestData creates a test user."""
        ValidBaseViewPermissionTest.setUpTestData()

        assert hasattr(ValidBaseViewPermissionTest, "user")
        assert ValidBaseViewPermissionTest.user.username == "test_user"


class BaseViewPermissionTestMixinGetViewInstanceTest(TestCase):
    """Tests for get_view_instance method."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create(username="instance_test_user", email="test@example.com")

    def setUp(self):
        self.test_case = ValidBaseViewPermissionTest("test_view_class_inherits_mixin")

    def test_get_view_instance_with_default_kwargs(self):
        """Test get_view_instance uses view_kwargs when kwargs is None."""
        view = self.test_case.get_view_instance(user=self.user)

        assert view.kwargs == {}
        assert view.request.user == self.user
        assert view.request.method == "GET"

    def test_get_view_instance_with_custom_kwargs(self):
        """Test get_view_instance uses provided kwargs."""
        custom_kwargs = {"pk": 123, "slug": "test-slug"}
        view = self.test_case.get_view_instance(user=self.user, kwargs=custom_kwargs)

        assert view.kwargs == custom_kwargs
        assert view.request.user == self.user

    def test_get_view_instance_with_different_method(self):
        """Test get_view_instance with different HTTP methods."""
        view = self.test_case.get_view_instance(user=self.user, method="POST")

        assert view.request.method == "POST"

    def test_get_view_instance_with_anonymous_user(self):
        """Test get_view_instance with AnonymousUser."""
        anonymous = AnonymousUser()
        view = self.test_case.get_view_instance(user=anonymous)

        assert view.request.user == anonymous

    def test_get_view_instance_with_custom_view_kwargs(self):
        """Test get_view_instance respects class-level view_kwargs when kwargs not provided."""

        class TestWithViewKwargs(BaseViewPermissionTestMixin, TestCase):
            view_class = TestViewWithPermissions
            permission_list = ("auth.change_user",)
            view_kwargs = {"pk": 456}

        test_instance = TestWithViewKwargs("test_view_class_inherits_mixin")
        ValidBaseViewPermissionTest.setUpTestData()
        view = test_instance.get_view_instance(user=self.user)

        assert view.kwargs == {"pk": 456}


class BaseViewPermissionTestMixinTestViewClassInheritsMixinTest(ValidBaseViewPermissionTest):
    """Tests for test_view_class_inherits_mixin method."""

    def test_view_class_inherits_mixin_positive(self):
        """Test that view_class correctly inherits from DjangoPermissionRequiredMixin."""
        # This should pass without raising any assertion errors
        self.test_view_class_inherits_mixin()

    def test_view_class_inherits_mixin_with_non_inheriting_class(self):
        """Test that assertion fails when view doesn't inherit the mixin."""

        class NonInheritingView(generic.View):
            pass

        class TestWithNonInheritingView(BaseViewPermissionTestMixin, TestCase):
            view_class = NonInheritingView
            permission_list = ("auth.change_user",)

        test_instance = TestWithNonInheritingView("test_view_class_inherits_mixin")

        with pytest.raises(AssertionError) as exc_info:
            test_instance.test_view_class_inherits_mixin()

        assert "False is not true" in str(exc_info.value)


class BaseViewPermissionTestMixinTestPermissionsAreEqualTest(TestCase):
    """Tests for test_permissions_are_equal method."""

    def test_permissions_are_equal_with_none_permission_list_in_test(self):
        """Test assertion when test class permission_list is None."""

        class TestWithNonePermissionList(BaseViewPermissionTestMixin, TestCase):
            view_class = TestViewWithPermissions
            permission_list = None

        test_instance = TestWithNonePermissionList("test_permissions_are_equal")

        with pytest.raises(AssertionError) as exc_info:
            test_instance.test_permissions_are_equal()

        assert "Missing permission list declaration in test" in str(exc_info.value)

    def test_permissions_are_equal_with_none_permission_list_in_view(self):
        """Test assertion when view class permission_list is None."""
        # We need to temporarily set permission_list to None to trigger the RuntimeError in __init__
        # But we can't do that because __init__ will fail. Instead, we'll mock the view_class attribute

        class TestWithNoneViewPermissionList(BaseViewPermissionTestMixin, TestCase):
            permission_list = ("auth.change_user",)

            # Create a mock view class that has permission_list as None but bypasses __init__ check
            @property
            def view_class(self):
                mock_view = mock.MagicMock()
                mock_view.permission_list = None
                return mock_view

            # Override __init__ to bypass view_class check
            def __init__(self, *args, **kwargs):
                TestCase.__init__(self, *args, **kwargs)

        test_instance = TestWithNoneViewPermissionList("test_permissions_are_equal")

        with pytest.raises(AssertionError) as exc_info:
            test_instance.test_permissions_are_equal()

        assert "Missing permission list declaration in view" in str(exc_info.value)

    def test_permissions_are_equal_with_different_count(self):
        """Test assertion when permission counts differ."""

        class TestWithDifferentCount(BaseViewPermissionTestMixin, TestCase):
            view_class = TestViewMultiplePermissions
            permission_list = ("auth.change_user",)  # Only one, but view has two

        test_instance = TestWithDifferentCount("test_permissions_are_equal")

        with pytest.raises(AssertionError) as exc_info:
            test_instance.test_permissions_are_equal()

        assert "1 != 2" in str(exc_info.value)

    def test_permissions_are_equal_with_different_permissions(self):
        """Test assertion when permissions are different."""

        class TestWithDifferentPermissions(BaseViewPermissionTestMixin, TestCase):
            view_class = TestViewWithPermissions
            permission_list = ("auth.add_user",)  # Different permission

        test_instance = TestWithDifferentPermissions("test_permissions_are_equal")

        with pytest.raises(AssertionError) as exc_info:
            test_instance.test_permissions_are_equal()

        assert "'auth.add_user' not found in" in str(exc_info.value)

    def test_permissions_are_equal_with_matching_permissions(self):
        """Test that matching permissions pass the assertion."""
        test_instance = ValidBaseViewPermissionTest("test_permissions_are_equal")
        ValidBaseViewPermissionTest.setUpTestData()

        # Should not raise any assertion errors
        test_instance.test_permissions_are_equal()

    def test_permissions_are_equal_with_multiple_permissions(self):
        """Test that multiple matching permissions pass the assertion."""
        test_instance = ValidMultiplePermissionsTest("test_permissions_are_equal")
        ValidMultiplePermissionsTest.setUpTestData()

        # Should not raise any assertion errors
        test_instance.test_permissions_are_equal()


class BaseViewPermissionTestMixinTestPermissionsExistInDatabaseTest(TestCase):
    """Tests for test_permissions_exist_in_database method."""

    def test_permissions_exist_with_ill_formatted_permission(self):
        """Test that ill-formatted permissions (without '.') raise TestSetupConfigurationError."""

        class TestWithIllFormattedPermission(BaseViewPermissionTestMixin, TestCase):
            view_class = TestViewWithPermissions
            permission_list = ("invalid_permission_without_dot",)

        test_instance = TestWithIllFormattedPermission("test_permissions_exist_in_database")

        with pytest.raises(TestSetupConfigurationError) as exc_info:
            test_instance.test_permissions_exist_in_database()

        assert 'contains ill-formatted permission "invalid_permission_without_dot"' in str(exc_info.value)

    def test_permissions_exist_with_nonexistent_permission(self):
        """Test that non-existent permissions raise TestSetupConfigurationError."""

        class TestWithNonexistentPermission(BaseViewPermissionTestMixin, TestCase):
            view_class = TestViewWithPermissions
            permission_list = ("nonexistent_app.nonexistent_permission",)

        test_instance = TestWithNonexistentPermission("test_permissions_exist_in_database")

        with pytest.raises(TestSetupConfigurationError) as exc_info:
            test_instance.test_permissions_exist_in_database()

        assert 'contains invalid permission "nonexistent_app.nonexistent_permission"' in str(exc_info.value)

    def test_permissions_exist_with_valid_permissions(self):
        """Test that valid permissions pass the validation."""
        test_instance = ValidBaseViewPermissionTest("test_permissions_exist_in_database")
        ValidBaseViewPermissionTest.setUpTestData()

        # Should not raise any errors
        test_instance.test_permissions_exist_in_database()

    def test_permissions_exist_with_multiple_valid_permissions(self):
        """Test that multiple valid permissions pass the validation."""
        test_instance = ValidMultiplePermissionsTest("test_permissions_exist_in_database")
        ValidMultiplePermissionsTest.setUpTestData()

        # Should not raise any errors
        test_instance.test_permissions_exist_in_database()


class BaseViewPermissionTestMixinTestPassesLoginBarrierIsCalledTest(ValidBaseViewPermissionTest):
    """Tests for test_passes_login_barrier_is_called method."""

    def test_passes_login_barrier_is_called_verifies_method_call(self):
        """Test that passes_login_barrier is actually called during dispatch."""
        # This test verifies the mocking behavior works correctly
        self.test_passes_login_barrier_is_called()

    def test_passes_login_barrier_is_called_returns_302(self):
        """Test that when passes_login_barrier returns False, we get a 302 redirect."""
        with mock.patch.object(self.view_class, "passes_login_barrier", return_value=False):
            view = self.get_view_instance(user=AnonymousUser())
            response = view.dispatch(request=view.request, **view.kwargs)
            assert response.status_code == 302


class BaseViewPermissionTestMixinTestHasPermissionsIsCalledTest(ValidBaseViewPermissionTest):
    """Tests for test_has_permissions_is_called method."""

    def test_has_permissions_is_called_verifies_method_call(self):
        """Test that has_permissions is actually called during dispatch."""
        # This test verifies the mocking behavior works correctly
        self.test_has_permissions_is_called()

    def test_has_permissions_is_called_returns_403(self):
        """Test that when has_permissions returns False, we get a 403 forbidden."""
        with mock.patch.object(self.view_class, "has_permissions", return_value=False):
            view = self.get_view_instance(user=self.user)
            response = view.dispatch(request=view.request, **view.kwargs)
            assert response.status_code == 403


class BaseViewPermissionTestMixinIntegrationTest(ValidBaseViewPermissionTest):
    """Integration tests for BaseViewPermissionTestMixin."""

    def test_full_workflow_with_valid_setup(self):
        """Test that a properly configured test case passes all checks."""
        # All inherited test methods should pass
        self.test_view_class_inherits_mixin()
        self.test_permissions_are_equal()
        self.test_permissions_exist_in_database()
        self.test_passes_login_barrier_is_called()
        self.test_has_permissions_is_called()

    def test_view_instance_creation_and_dispatch(self):
        """Test creating a view instance and dispatching a request."""
        # Create view with proper permissions
        perm = Permission.objects.get(content_type__app_label="auth", codename="change_user")
        self.user.user_permissions.add(perm)

        view = self.get_view_instance(user=self.user)
        response = view.dispatch(request=view.request, **view.kwargs)

        assert response.status_code == 200

    def test_view_instance_creation_without_permissions(self):
        """Test creating a view instance without required permissions."""
        # User doesn't have the required permission
        view = self.get_view_instance(user=self.user)
        response = view.dispatch(request=view.request, **view.kwargs)

        assert response.status_code == 403

    def test_view_instance_creation_with_anonymous_user(self):
        """Test creating a view instance with anonymous user."""
        view = self.get_view_instance(user=AnonymousUser())
        response = view.dispatch(request=view.request, **view.kwargs)

        # Should redirect to login
        assert response.status_code == 302
