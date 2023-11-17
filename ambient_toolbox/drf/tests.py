from django.contrib.auth.models import AbstractUser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.viewsets import GenericViewSet


class BaseViewSetTestMixin:
    """
    Base test mixin to lower the pain of testing API calls. Focuses on ViewSets.
    """

    default_api_user = None
    view_class = None

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        # Create test factory
        cls.factory = APIRequestFactory()

    def setUp(self) -> None:
        super().setUp()

        # Create API user with proper permissions
        self.default_api_user = self.get_default_api_user()

    def get_default_api_user(self) -> AbstractUser:
        """
        Method to create the API request user in.
        """
        raise NotImplementedError

    def validate_authentication_required(self, *, url: str, method: str, view: str):
        """
        Helper method to quickly ensure that a given view needs authorisation.
        """
        response = self.execute_request(method=method, url=url, viewset_kwargs={method: view})

        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def execute_request(  # noqa: PLR0913
        self,
        *,
        url,
        view_kwargs=None,
        method="get",
        data=None,
        view_class=None,
        user=None,
        viewset_kwargs=None,
        data_format="json",
    ) -> Response:
        """
        Helper method which wraps all relevant setup to execute a request to the backends api

        view_kwargs: Kwargs from the URL (need to be passed manually to the view class as well)
        method: Request method (get, post, delete...)
        data: Dict of data to pass to the request, usually for post, put, patch
        view_class: Will overwrite the classes default view_class if set
        user: User to authenticate the request with. If no user is set, there will be no authentication
        viewset_kwargs: ViewSets need a dict to tell it, what action we want to execute
        data_format: Format of the sent data, defaults to JSON, might be "multipart" etc.
        """

        # Set proper default fallback value for dicts
        if view_kwargs is None:
            view_kwargs = {}
        if viewset_kwargs is None:
            viewset_kwargs = {}

        # Create request
        request = getattr(self.factory, method)(path=url, data=data, format=data_format)

        # Authentication
        if user:
            force_authenticate(request, user=user)

        # Check if we want to override the view class for this single call
        view_class = view_class if view_class else self.view_class

        # Add viewset kwargs if we have a viewset here
        if isinstance(view_class(), GenericViewSet):
            view = view_class.as_view(viewset_kwargs)
        else:
            view = view_class.as_view()

        # Get response
        response = view(request, **view_kwargs)

        # Return response
        return response
